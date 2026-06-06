import fitz  # PyMuPDF
from typing import Dict, Any, Optional
from datetime import datetime

class PDFParserError(Exception):
    """Custom exception for PDF parsing errors"""
    pass

class PDFParser:
    """Production-grade PDF parser using PyMuPDF (fitz)"""
    
    def __init__(self):
        self.supported_mime_types = ["application/pdf"]
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse PDF file and extract text and metadata.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
            
        Raises:
            PDFParserError: If PDF parsing fails
        """
        try:
            doc = fitz.open(file_path)
            
            # Extract metadata
            metadata = {
                "page_count": len(doc),
                "author": doc.metadata.get("author", ""),
                "title": doc.metadata.get("title", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "modification_date": doc.metadata.get("modDate", ""),
            }
            
            # Extract text from all pages
            text_content = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text_content.append(page.get_text())
            
            full_text = "\n".join(text_content)
            
            doc.close()
            
            return {
                "text": full_text,
                "metadata": metadata,
                "parsed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise PDFParserError(f"Failed to parse PDF: {str(e)}")
    
    def is_supported(self, mime_type: str) -> bool:
        """Check if the MIME type is supported"""
        return mime_type in self.supported_mime_types
