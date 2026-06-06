from pydantic import BaseModel
from typing import List

class ClassificationResult(BaseModel):
    document_type: str
    confidence: float
    matched_rules: List[str]
