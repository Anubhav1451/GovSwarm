import re
from typing import Dict, List, Any
from datetime import datetime

class EntityExtractor:
    """Production-grade entity extractor with compiled regex patterns"""
    
    def __init__(self):
        # Compile regex patterns for performance
        self.gstin_pattern = re.compile(
            r'\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b',
            re.IGNORECASE
        )
        self.pan_pattern = re.compile(
            r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
            re.IGNORECASE
        )
        self.cin_pattern = re.compile(
            r'\b[LU|UN|TN|MH|KA|DL|UP|WB|GJ|RJ|MP|OR|KA]{2}[0-9]{5}[A-Z]{2}[0-9]{4}\b',
            re.IGNORECASE
        )
        self.date_pattern = re.compile(
            r'\b(?:0[1-9]|[12][0-9]|3[01])[-/](?:0[1-9]|1[012])[-/]\d{4}\b|\b\d{4}[-/](?:0[1-9]|1[012])[-/](?:0[1-9]|[12][0-9]|3[01])\b'
        )
        self.organization_pattern = re.compile(
            r'\b(?:[A-Z][a-z]+\s+){1,4}(?:Private\s+Limited|Public\s+Limited|Ltd|Pvt\.?|LLC|Inc|Corp|Corporation|Enterprise|Technologies|Solutions|Systems|Group|Industries)\b',
            re.IGNORECASE
        )
    
    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from text using compiled regex patterns.
        
        Args:
            text: Text content to extract entities from
            
        Returns:
            Dictionary containing extracted entities
        """
        # Extract GSTIN numbers
        gstins = list(set(self.gstin_pattern.findall(text)))
        
        # Extract PAN numbers
        pans = list(set(self.pan_pattern.findall(text)))
        
        # Extract CIN numbers
        cins = list(set(self.cin_pattern.findall(text)))
        
        # Extract dates
        dates = list(set(self.date_pattern.findall(text)))
        
        # Extract organization names
        organization_names = list(set(self.organization_pattern.findall(text)))
        
        return {
            "gstins": gstins,
            "pans": pans,
            "cins": cins,
            "organization_names": organization_names,
            "registration_dates": dates
        }
    
    def extract_with_confidence(self, text: str) -> Dict[str, Any]:
        """
        Extract entities with confidence scores and metadata.
        
        Args:
            text: Text content to extract entities from
            
        Returns:
            Dictionary containing extracted entities with metadata
        """
        entities = self.extract(text)
        
        return {
            "entities": entities,
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "total_entities": sum(len(v) for v in entities.values()),
            "entity_types": [k for k, v in entities.items() if v]
        }
