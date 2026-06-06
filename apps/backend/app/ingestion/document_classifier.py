from app.schemas.classification import ClassificationResult

class DocumentClassifier:
    """Document classifier using rule-based engine for compliance intelligence"""
    
    @staticmethod
    def classify_document(extracted_text: str, entities: dict) -> ClassificationResult:
        """
        Classify document based on extracted text and entities using rule engine.
        
        Args:
            extracted_text: Text content extracted from document
            entities: Dictionary containing extracted entities (gstins, pans, cins, etc.)
            
        Returns:
            ClassificationResult with document_type, confidence, and matched_rules
        """
        text_upper = extracted_text.upper()
        matched_rules = []
        confidence = 0.0
        document_type = "UNKNOWN"
        
        # GST_CERTIFICATE Rules
        gst_keywords = ["GOODS AND SERVICES TAX", "GST REGISTRATION", "REGISTRATION CERTIFICATE"]
        gst_score = 0
        gst_matched = []
        
        for keyword in gst_keywords:
            if keyword in text_upper:
                gst_score += 30
                gst_matched.append(f"GST_KEYWORD: {keyword}")
        
        if entities.get("gstins"):
            gst_score += 50
            gst_matched.append(f"GSTIN_FOUND: {len(entities['gstins'])} GSTIN(s)")
        
        if gst_score > 0:
            matched_rules.extend(gst_matched)
            confidence = max(confidence, gst_score)
            document_type = "GST_CERTIFICATE"
        
        # PAN_CARD Rules
        pan_keywords = ["INCOME TAX DEPARTMENT", "PERMANENT ACCOUNT NUMBER", "PAN"]
        pan_score = 0
        pan_matched = []
        
        for keyword in pan_keywords:
            if keyword in text_upper:
                pan_score += 30
                pan_matched.append(f"PAN_KEYWORD: {keyword}")
        
        if entities.get("pans"):
            pan_score += 50
            pan_matched.append(f"PAN_FOUND: {len(entities['pans'])} PAN(s)")
        
        if pan_score > 0:
            matched_rules.extend(pan_matched)
            confidence = max(confidence, pan_score)
            document_type = "PAN_CARD"
        
        # CIN_CERTIFICATE Rules
        cin_keywords = ["CORPORATE IDENTIFICATION NUMBER", "MINISTRY OF CORPORATE AFFAIRS", "CERTIFICATE OF INCORPORATION"]
        cin_score = 0
        cin_matched = []
        
        for keyword in cin_keywords:
            if keyword in text_upper:
                cin_score += 30
                cin_matched.append(f"CIN_KEYWORD: {keyword}")
        
        if entities.get("cins"):
            cin_score += 50
            cin_matched.append(f"CIN_FOUND: {len(entities['cins'])} CIN(s)")
        
        if cin_score > 0:
            matched_rules.extend(cin_matched)
            confidence = max(confidence, cin_score)
            document_type = "CIN_CERTIFICATE"
        
        # Cap confidence at 100
        confidence = min(confidence, 100.0)
        
        # If no rules hit or confidence below 50, return UNKNOWN
        if confidence < 50.0:
            document_type = "UNKNOWN"
            confidence = 0.0
            matched_rules = []
        
        return ClassificationResult(
            document_type=document_type,
            confidence=confidence,
            matched_rules=matched_rules
        )
