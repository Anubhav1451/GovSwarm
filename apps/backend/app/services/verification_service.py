import asyncio
from sqlalchemy.orm import Session
from app.models.verification_result import VerificationResult as VerificationResultModel
from app.integrations.registry_client import RegistryClient
from app.services.audit_service import AuditService

class VerificationService:
    """Service for verifying identifiers against government registries"""
    
    @staticmethod
    async def verify_and_persist_identifiers(db: Session, document_id: int, entities: dict):
        """
        Verify extracted identifiers against government registries and persist results.
        
        Args:
            db: Database session
            document_id: ID of the document being verified
            entities: Dictionary containing extracted entities (gstins, pans, cins)
        """
        registry_client = RegistryClient()
        
        # Verify GSTINs
        for gstin in entities.get("gstins", []):
            verification_result = await registry_client.verify_gstin(gstin)
            
            # Persist verification result
            verification_record = VerificationResultModel(
                document_id=document_id,
                verification_type=verification_result.verification_type,
                verification_status=verification_result.status,
                response_payload=verification_result.payload
            )
            db.add(verification_record)
            
            # Audit log injection
            AuditService.log_action(
                db=db,
                actor_id="system",
                action="EXTERNAL_REGISTRY_VERIFIED",
                resource_type="verification_result",
                resource_id=str(verification_record.id),
                metadata={
                    "identifier": verification_result.identifier,
                    "verification_type": verification_result.verification_type,
                    "found": verification_result.found,
                    "status": verification_result.status
                }
            )
        
        # Verify PANs
        for pan in entities.get("pans", []):
            verification_result = await registry_client.verify_pan(pan)
            
            # Persist verification result
            verification_record = VerificationResultModel(
                document_id=document_id,
                verification_type=verification_result.verification_type,
                verification_status=verification_result.status,
                response_payload=verification_result.payload
            )
            db.add(verification_record)
            
            # Audit log injection
            AuditService.log_action(
                db=db,
                actor_id="system",
                action="EXTERNAL_REGISTRY_VERIFIED",
                resource_type="verification_result",
                resource_id=str(verification_record.id),
                metadata={
                    "identifier": verification_result.identifier,
                    "verification_type": verification_result.verification_type,
                    "found": verification_result.found,
                    "status": verification_result.status
                }
            )
        
        # Verify CINs
        for cin in entities.get("cins", []):
            verification_result = await registry_client.verify_cin(cin)
            
            # Persist verification result
            verification_record = VerificationResultModel(
                document_id=document_id,
                verification_type=verification_result.verification_type,
                verification_status=verification_result.status,
                response_payload=verification_result.payload
            )
            db.add(verification_record)
            
            # Audit log injection
            AuditService.log_action(
                db=db,
                actor_id="system",
                action="EXTERNAL_REGISTRY_VERIFIED",
                resource_type="verification_result",
                resource_id=str(verification_record.id),
                metadata={
                    "identifier": verification_result.identifier,
                    "verification_type": verification_result.verification_type,
                    "found": verification_result.found,
                    "status": verification_result.status
                }
            )
        
        # Commit all verification results
        db.commit()

# Singleton instance
verification_service = VerificationService()
