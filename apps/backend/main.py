from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import shutil
import os

app = FastAPI(title="GovSwarm Multi-Agent AI Auditor API", version="2.0.0")

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

# In-memory state for last processed document metadata
last_document_metadata = {
    "filename": None,
    "organizationName": None,
    "incorporationNumber": None,
    "complianceStatus": None,
    "extracted_name": None
}

# ============================================================================
# MULTI-AGENT SYSTEM CORE
# ============================================================================

class GovSwarmLegalSpecialist:
    """Agent 1: Specialized in legal document review and corporate bylaws analysis"""
    
    def __init__(self):
        self.name = "GovSwarm Legal Specialist"
        self.expertise = ["corporate bylaws", "legal compliance", "document verification"]
    
    def review_document(self, metadata: dict) -> str:
        """Review uploaded document and provide legal assessment"""
        org_name = metadata.get("organizationName", "Unknown Entity")
        status = metadata.get("complianceStatus", "UNKNOWN")
        
        if status == "VERIFIED":
            return f"I have reviewed the uploaded certificate for {org_name}. Corporate bylaws seem sound. Legal framework alignment confirmed."
        else:
            return f"I have reviewed the uploaded certificate for {org_name}. Additional legal documentation may be required for full verification."
    
    def assess_compliance_requirements(self) -> str:
        """Provide compliance checklist"""
        return "Legal requirements checklist: Valid incorporation certificate, corporate bylaws, tax identification, and regulatory filings must be present."

class GovSwarmComplianceAuditor:
    """Agent 2: Specialized in cross-referencing with government registry frameworks"""
    
    def __init__(self):
        self.name = "GovSwarm Compliance Auditor"
        self.expertise = ["registry cross-referencing", "compliance verification", "system status"]
    
    def cross_reference_registry(self, metadata: dict) -> str:
        """Cross-reference document data with government registry"""
        org_name = metadata.get("organizationName", "Unknown Entity")
        incorp_number = metadata.get("incorporationNumber", "UNKNOWN")
        status = metadata.get("complianceStatus", "UNKNOWN")
        
        if status == "VERIFIED":
            return f"Cross-referencing with Gov-Registry framework... Incorporation number {incorp_number} matches perfectly! System status updated to APPROVED."
        else:
            return f"Cross-referencing with Gov-Registry framework... Incorporation number {incorp_number} requires additional verification. System status: PENDING REVIEW."
    
    def verify_auto_fill_readiness(self, metadata: dict) -> str:
        """Verify if data is ready for auto-fill pipeline"""
        if metadata.get("organizationName") and metadata.get("incorporationNumber"):
            return "Document data is primed for Auto-Fill pipeline execution. All required fields are mapped."
        else:
            return "Document data incomplete. Please upload a valid document for Auto-Fill preparation."

# Initialize Multi-Agent System
legal_specialist = GovSwarmLegalSpecialist()
compliance_auditor = GovSwarmComplianceAuditor()

def generate_agent_conversation(intent: str, metadata: dict) -> str:
    """
    Generate simulated conversation between Legal Specialist and Compliance Auditor
    based on user intent and document metadata
    """
    if not metadata.get("filename"):
        return "🤖 [LEGAL AGENT]: No document has been uploaded yet. Please upload a certificate for review.\n🕵️‍♂️ [AUDITOR AGENT]: Awaiting document data to begin registry cross-referencing."
    
    legal_response = legal_specialist.review_document(metadata)
    compliance_response = compliance_auditor.cross_reference_registry(metadata)
    
    return f"🤖 [LEGAL AGENT]: {legal_response}\n🕵️‍♂️ [AUDITOR AGENT]: {compliance_response}"

def generate_agent_response(intent: str, metadata: dict) -> str:
    """
    Generate appropriate agent response based on intent
    """
    message_lower = intent.lower()
    
    # Document content query - trigger agent conversation
    if any(keyword in message_lower for keyword in ['document me kya mila', 'what was found', 'document content', 'what is in the document', 'kya mila']):
        return generate_agent_conversation(intent, metadata)
    
    # Auto-fill intent
    if any(keyword in message_lower for keyword in ['fill', 'auto-fill', 'autofill']):
        if metadata.get("filename"):
            legal_assessment = legal_specialist.review_document(metadata)
            compliance_check = compliance_auditor.verify_auto_fill_readiness(metadata)
            return f"🤖 [LEGAL AGENT]: {legal_assessment}\n🕵️‍♂️ [AUDITOR AGENT]: {compliance_check} Click the 'Auto-Fill Application Form' button to execute."
        else:
            return "🤖 [LEGAL AGENT]: No document data available for auto-fill.\n🕵️‍♂️ [AUDITOR AGENT]: Please upload a document first to parse the required fields."
    
    # Help/Compliance intent
    if any(keyword in message_lower for keyword in ['help', 'comply']):
        legal_checklist = legal_specialist.assess_compliance_requirements()
        return f"🤖 [LEGAL AGENT]: {legal_checklist}\n🕵️‍♂️ [AUDITOR AGENT]: Upload a document with 'gov', 'inc', or 'corp' in the filename for automatic verification."
    
    # Status/Eligibility intent
    if any(keyword in message_lower for keyword in ['status', 'eligibility']):
        if metadata.get("filename"):
            return f"🤖 [LEGAL AGENT]: Document review in progress for {metadata['organizationName']}.\n🕵️‍♂️ [AUDITOR AGENT]: Registry scanner active. Current status: {metadata['complianceStatus']}."
        else:
            return "🤖 [LEGAL AGENT]: Awaiting document upload for status assessment.\n🕵️‍♂️ [AUDITOR AGENT]: Registry scanner on standby. Upload a document to begin."
    
    # Default response
    return "🤖 [LEGAL AGENT]: GovSwarm Multi-Agent System ready. How can I assist with your compliance needs?\n🕵️‍♂️ [AUDITOR AGENT]: Registry framework operational. Upload documents for automated analysis."

# ============================================================================
# API ENDPOINTS
# ============================================================================

# Multi-Agent Chat Route (POST /api/chat)
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Process user query through multi-agent system and return simulated agent conversation.
    """
    try:
        agent_response = generate_agent_response(request.message, last_document_metadata)
        
        return {
            "status": "success",
            "response": agent_response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-agent chat processing failed: {str(e)}")

# Document Parsing Route with Agent Review Log (POST /api/upload)
@app.post("/api/upload")
async def upload_endpoint(file: UploadFile):
    """
    Ingest government files, simulate agent review process,
    and return compliance data for auto-fill action.
    """
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Real File-Name Parsing Logic - extract names from filename with smart formatting
        filename_lower = file.filename.lower()
        extracted_name = None
        
        # Check for specific user names or custom strings in filename
        name_keywords = ['screenshot', 'anubhav', 'gov', 'inc', 'corp']
        for keyword in name_keywords:
            if keyword in filename_lower:
                # Smart Enterprise Text Formatting - capitalize first letter of each word
                extracted_name = keyword.capitalize()
                break
        
        # Determine organization name dynamically with proper capitalization
        if extracted_name:
            # Format as capitalized company node (e.g., "Anubhav Enterprise")
            organization_name = f"{extracted_name} Enterprise"
            incorp_number = f"INCORP-2026-{extracted_name[:3].upper()}X"
            compliance_status = "VERIFIED"
        else:
            organization_name = "Unknown Entity Detected"
            incorp_number = "PENDING_REGISTRATION"
            compliance_status = "REVIEW_REQUIRED"
        
        # Simulate Agent Review Log
        agent_review_log = {
            "legal_specialist_review": legal_specialist.review_document({
                "organizationName": organization_name,
                "complianceStatus": compliance_status
            }),
            "compliance_auditor_check": compliance_auditor.cross_reference_registry({
                "organizationName": organization_name,
                "incorporationNumber": incorp_number,
                "complianceStatus": compliance_status
            })
        }
        
        # Update in-memory state with last processed document metadata
        last_document_metadata["filename"] = file.filename
        last_document_metadata["organizationName"] = organization_name
        last_document_metadata["incorporationNumber"] = incorp_number
        last_document_metadata["complianceStatus"] = compliance_status
        last_document_metadata["extracted_name"] = extracted_name
        
        # Return parsed configuration for frontend form layout
        return {
            "status": "success",
            "data": {
                "organizationName": organization_name,
                "incorporationNumber": incorp_number,
                "complianceStatus": compliance_status
            },
            "agent_review": agent_review_log
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

# Health Check Endpoint
@app.get("/api/health")
async def health_check():
    """
    Health check endpoint to verify API status.
    """
    return {
        "status": "healthy",
        "service": "GovSwarm Multi-Agent AI Auditor API",
        "version": "2.0.0",
        "agents": ["GovSwarm Legal Specialist", "GovSwarm Compliance Auditor"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
