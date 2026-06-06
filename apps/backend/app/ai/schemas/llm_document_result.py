from pydantic import BaseModel
from typing import Optional

class LLMDocumentResult(BaseModel):
    document_type: str
    confidence: float
    organization_name: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    cin: Optional[str] = None
    reasoning: str
