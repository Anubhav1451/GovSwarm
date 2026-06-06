import os
import json
from typing import Dict
from openai import OpenAI
from app.ai.schemas.llm_document_result import LLMDocumentResult
from app.ai.prompts.document_classifier_prompt import DOCUMENT_CLASSIFIER_PROMPT

class LLMFallback:
    """Intelligent LLM fallback client for document classification"""
    
    @staticmethod
    def classify_unknown_document(text: str, metadata: dict, entities: dict) -> LLMDocumentResult:
        """
        Classify unknown document using LLM fallback.
        
        Args:
            text: Document text content
            metadata: Document metadata
            entities: Extracted entities
            
        Returns:
            LLMDocumentResult with classification result
        """
        try:
            # Token Saving Guardrail: Truncate input text intelligently
            max_length = 7000
            if len(text) > max_length:
                # Take first 5000 and last 2000 characters
                truncated_text = text[:5000] + text[-2000:]
            else:
                truncated_text = text
            
            # Format prompt with context
            prompt = DOCUMENT_CLASSIFIER_PROMPT.format(
                text=truncated_text,
                metadata=json.dumps(metadata, indent=2),
                entities=json.dumps(entities, indent=2)
            )
            
            # Initialize OpenAI client
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            client = OpenAI(api_key=api_key)
            
            # Call OpenAI API with structured output
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a deterministic KYC metadata auditor. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format=LLMDocumentResult,
                temperature=0.0
            )
            
            # Parse response into LLMDocumentResult
            result = response.choices[0].message.parsed
            
            return result
            
        except Exception as e:
            # Return safe graceful fallback payload on failure
            return LLMDocumentResult(
                document_type="UNKNOWN_FAILED",
                confidence=0.0,
                organization_name=None,
                gstin=None,
                pan=None,
                cin=None,
                reasoning=f"LLM fallback failed: {str(e)}"
            )
