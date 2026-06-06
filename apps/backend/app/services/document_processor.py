from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.ingestion import ExtractionResult
from app.ingestion.pdf_parser import PDFParser, PDFParserError
from app.ingestion.entity_extractor import EntityExtractor
from app.ingestion.document_classifier import DocumentClassifier
from app.models.document import ProcessingStatus
from app.services.audit_service import AuditService
from app.services.verification_service import VerificationService
from app.services.evaluation_service import EvaluationService
from app.ai.llm_fallback import LLMFallback
import json
import asyncio

class DocumentProcessor:
    """Master Document Processor Orchestrator"""
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.entity_extractor = EntityExtractor()
    
    def process_document(self, db: Session, document_id: int, file_path: str) -> Document:
        """
        Orchestrate the complete document processing cycle.
        
        Args:
            db: Database session
            document_id: ID of the document to process
            file_path: Path to the file to process
            
        Returns:
            Updated document record
            
        Raises:
            PDFParserError: If PDF parsing fails
            Exception: If processing fails
        """
        try:
            # Step 1: Retrieve document from database
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise ValueError(f"Document with ID {document_id} not found")
            
            # Step 2: Parse PDF to extract text and metadata
            parse_result = self.pdf_parser.parse(file_path)
            text_content = parse_result["text"]
            metadata = parse_result["metadata"]
            
            # Step 3: Extract entities from text
            entities = self.entity_extractor.extract(text_content)
            
            # Step 4: Classify document using rule-based engine
            classification_result = DocumentClassifier.classify_document(text_content, entities)
            
            # Step 4.5: LLM Fallback Gateway - Check if rule-based confidence is low or unknown
            if classification_result.document_type == "UNKNOWN" or classification_result.confidence < 60.0:
                # Inject system audit marker before calling LLM
                AuditService.log_action(
                    db=db,
                    actor_id=document.uploaded_by or "system",
                    action="LLM_FALLBACK_TRIGGERED",
                    resource_type="document",
                    resource_id=str(document.id),
                    metadata={
                        "original_document_type": classification_result.document_type,
                        "original_confidence": classification_result.confidence,
                        "reason": "Rule-based classification confidence below threshold"
                    }
                )
                
                # Fire the fallback extraction
                llm_fallback_res = LLMFallback.classify_unknown_document(text_content, metadata, entities)
                
                # If LLM successfully re-classified with confidence >= 60, override
                if llm_fallback_res.confidence >= 60.0:
                    classification_result.document_type = llm_fallback_res.document_type
                    classification_result.confidence = llm_fallback_res.confidence
                    classification_result.matched_rules.append(f"LLM_FALLBACK_SUCCESS: {llm_fallback_res.reasoning}")
                    
                    # Safely inject any discovered entity overrides back into extraction keys
                    if llm_fallback_res.gstin and llm_fallback_res.gstin not in entities["gstins"]:
                        entities["gstins"].append(llm_fallback_res.gstin)
                    if llm_fallback_res.pan and llm_fallback_res.pan not in entities["pans"]:
                        entities["pans"].append(llm_fallback_res.pan)
                    if llm_fallback_res.cin and llm_fallback_res.cin not in entities["cins"]:
                        entities["cins"].append(llm_fallback_res.cin)
                    if llm_fallback_res.organization_name and llm_fallback_res.organization_name not in entities["organization_names"]:
                        entities["organization_names"].append(llm_fallback_res.organization_name)
            
            # Step 5: Load entities into Pydantic model for type safety
            extraction_result = ExtractionResult(
                gstins=entities["gstins"],
                pans=entities["pans"],
                cins=entities["cins"],
                organization_names=entities["organization_names"],
                registration_dates=entities["registration_dates"]
            )
            
            # Step 6: Update document metadata
            document.page_count = metadata.get("page_count", 0)
            document.author = metadata.get("author", "")
            document.title = metadata.get("title", "")
            document.storage_path = file_path
            document.document_type = classification_result.document_type
            
            # Step 7: Create or update document_metadata record
            # For now, we'll store extracted data in a JSON field
            # In a full implementation, this would be a separate table
            document.extracted_text = text_content
            document.extracted_entities = json.dumps(extraction_result.model_dump())
            
            # Step 8: Update processing status to completed
            document.processing_status = ProcessingStatus.COMPLETED
            
            # Commit changes
            db.commit()
            db.refresh(document)
            
            # Audit Log Injection: Document Classified
            AuditService.log_action(
                db=db,
                actor_id=document.uploaded_by or "system",
                action="DOCUMENT_CLASSIFIED",
                resource_type="document",
                resource_id=str(document.id),
                metadata={
                    "document_type": classification_result.document_type,
                    "confidence": classification_result.confidence,
                    "matched_rules": classification_result.matched_rules
                }
            )
            
            # Scenario C: Parse Success - Log audit with entity counts
            AuditService.log_action(
                db=db,
                actor_id=document.uploaded_by or "system",
                action="PARSE_DOCUMENT_SUCCESS",
                resource_type="document",
                resource_id=str(document.id),
                metadata={
                    "page_count": document.page_count,
                    "gstins_count": len(extraction_result.gstins),
                    "pans_count": len(extraction_result.pans),
                    "cins_count": len(extraction_result.cins),
                    "organization_names_count": len(extraction_result.organization_names),
                    "registration_dates_count": len(extraction_result.registration_dates)
                }
            )
            
            # Step 9: Verify identifiers against government registries
            asyncio.run(VerificationService.verify_and_persist_identifiers(db, document_id, entities))
            
            # Step 10: Run compliance evaluation and risk scoring
            evaluation_result = EvaluationService.evaluate_document(db, document_id)
            
            return document
            
        except PDFParserError as e:
            # Update processing status to failed
            document.processing_status = ProcessingStatus.FAILED
            db.commit()
            
            # Scenario D: Parse Failure - Log audit before re-raising
            AuditService.log_action(
                db=db,
                actor_id=document.uploaded_by or "system",
                action="PARSE_DOCUMENT_FAILED",
                resource_type="document",
                resource_id=str(document.id),
                metadata={
                    "error_message": str(e),
                    "file_path": file_path
                }
            )
            
            raise
        except Exception as e:
            # Update processing status to failed
            if document:
                document.processing_status = ProcessingStatus.FAILED
                db.commit()
                
                # Scenario D: Parse Failure - Log audit before re-raising
                AuditService.log_action(
                    db=db,
                    actor_id=document.uploaded_by or "system",
                    action="PARSE_DOCUMENT_FAILED",
                    resource_type="document",
                    resource_id=str(document.id),
                    metadata={
                        "error_message": str(e),
                        "file_path": file_path
                    }
                )
                
            raise Exception(f"Document processing failed: {str(e)}")

# Singleton instance
document_processor = DocumentProcessor()
