from pydantic import BaseModel
from typing import List

class ExtractionResult(BaseModel):
    gstins: List[str]
    pans: List[str]
    cins: List[str]
    organization_names: List[str]
    registration_dates: List[str]
