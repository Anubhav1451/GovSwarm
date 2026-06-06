import asyncio
from app.schemas.verification import VerificationResult
from app.integrations.mock_registries import MOCK_GST_DB, MOCK_PAN_DB, MOCK_MCA_DB

class RegistryClient:
    """Client for verifying identifiers against government registries"""
    
    async def verify_gstin(self, gstin: str) -> VerificationResult:
        """
        Verify GSTIN against mock GST registry.
        
        Args:
            gstin: GSTIN identifier to verify
            
        Returns:
            VerificationResult with verification details
        """
        # Clean identifier
        cleaned_gstin = gstin.strip().upper()
        
        # Check against mock DB
        if cleaned_gstin in MOCK_GST_DB:
            return VerificationResult(
                identifier=cleaned_gstin,
                verification_type="GST",
                found=True,
                status="Active",
                payload=MOCK_GST_DB[cleaned_gstin]
            )
        else:
            return VerificationResult(
                identifier=cleaned_gstin,
                verification_type="GST",
                found=False,
                status="Not Found",
                payload={}
            )
    
    async def verify_pan(self, pan: str) -> VerificationResult:
        """
        Verify PAN against mock PAN registry.
        
        Args:
            pan: PAN identifier to verify
            
        Returns:
            VerificationResult with verification details
        """
        # Clean identifier
        cleaned_pan = pan.strip().upper()
        
        # Check against mock DB
        if cleaned_pan in MOCK_PAN_DB:
            return VerificationResult(
                identifier=cleaned_pan,
                verification_type="PAN",
                found=True,
                status="Active",
                payload=MOCK_PAN_DB[cleaned_pan]
            )
        else:
            return VerificationResult(
                identifier=cleaned_pan,
                verification_type="PAN",
                found=False,
                status="Not Found",
                payload={}
            )
    
    async def verify_cin(self, cin: str) -> VerificationResult:
        """
        Verify CIN against mock MCA registry.
        
        Args:
            cin: CIN identifier to verify
            
        Returns:
            VerificationResult with verification details
        """
        # Clean identifier
        cleaned_cin = cin.strip().upper()
        
        # Check against mock DB
        if cleaned_cin in MOCK_MCA_DB:
            return VerificationResult(
                identifier=cleaned_cin,
                verification_type="CIN",
                found=True,
                status="Active",
                payload=MOCK_MCA_DB[cleaned_cin]
            )
        else:
            return VerificationResult(
                identifier=cleaned_cin,
                verification_type="CIN",
                found=False,
                status="Not Found",
                payload={}
            )
