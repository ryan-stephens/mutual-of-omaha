"""
Bedrock service for AI-powered medical data extraction
"""

import boto3
import json
from botocore.exceptions import ClientError
from app.config import settings
from app.models.schemas import MedicalData
from app.services.prompt_manager import get_prompt_manager
import logging
from typing import Optional, Dict
import time

logger = logging.getLogger(__name__)


class BedrockService:
    """Service for interacting with AWS Bedrock"""
    
    def __init__(self):
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=settings.AWS_REGION
        )
        self.model_id = settings.BEDROCK_MODEL_ID
    
    def extract_medical_data(
        self,
        document_text: str,
        prompt_version: str = "v1"
    ) -> tuple[Optional[MedicalData], Dict[str, int], int]:
        """
        Extract structured medical data from document text
        
        Args:
            document_text: Raw text from medical document
            prompt_version: Version of extraction prompt to use
            
        Returns:
            Tuple of (MedicalData, token_usage, processing_time_ms)
        """
        start_time = time.time()
        
        try:
            prompt = self._build_extraction_prompt(document_text, prompt_version)
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "temperature": 0.1,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            
            logger.info(f"Invoking Bedrock model: {self.model_id}")
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            
            extracted_text = response_body['content'][0]['text']
            token_usage = {
                'input_tokens': response_body['usage']['input_tokens'],
                'output_tokens': response_body['usage']['output_tokens']
            }
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            medical_data = self._parse_extraction_result(extracted_text)
            
            logger.info(
                f"Extraction completed in {processing_time_ms}ms. "
                f"Tokens: {token_usage['input_tokens']} in, {token_usage['output_tokens']} out"
            )
            
            return medical_data, token_usage, processing_time_ms
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Bedrock invocation failed: {error_code} - {error_message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during extraction: {e}")
            raise
    
    def _build_extraction_prompt(self, document_text: str, version: str = "v1") -> str:
        """
        Build extraction prompt with specified version using PromptManager
        
        Args:
            document_text: Raw document text
            version: Prompt version (e.g., "v1.0.0", "v2.0.0")
            
        Returns:
            Formatted prompt string
        """
        try:
            prompt_manager = get_prompt_manager()
            
            # Map legacy version names to new format
            version_map = {
                "v1": "v1.0.0",
                "v2": "v2.0.0"
            }
            versioned_name = version_map.get(version, version)
            
            prompt = prompt_manager.format_prompt(document_text, versioned_name)
            logger.info(f"Using prompt version: {versioned_name}")
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to load prompt version {version}: {e}")
            # Fallback to inline prompt if PromptManager fails
            logger.warning("Falling back to inline prompt")
            return f"""You are a medical data extraction specialist. Extract structured information from the following medical document.

Extract in valid JSON format:
{{
  "patient_name": "Full patient name",
  "date_of_birth": "DOB in YYYY-MM-DD format",
  "diagnoses": ["List of medical diagnoses"],
  "medications": ["List of medications with dosages"],
  "lab_values": {{"test_name": "result with units"}},
  "procedures": ["List of medical procedures"],
  "allergies": ["List of known allergies"],
  "vital_signs": {{"vital_name": "value with units"}},
  "notes": "Any additional relevant information"
}}

Medical Document:
{document_text}

Return ONLY the JSON object, no additional text."""
    
    def _parse_extraction_result(self, extracted_text: str) -> Optional[MedicalData]:
        """
        Parse JSON extraction result into MedicalData object
        
        Args:
            extracted_text: JSON string from Bedrock
            
        Returns:
            MedicalData object or None if parsing fails
        """
        try:
            extracted_text = extracted_text.strip()
            
            logger.info(f"Raw extracted text (first 500 chars): {extracted_text[:500]}")
            
            if extracted_text.startswith('```json'):
                extracted_text = extracted_text[7:]
            if extracted_text.startswith('```'):
                extracted_text = extracted_text[3:]
            if extracted_text.endswith('```'):
                extracted_text = extracted_text[:-3]
            
            extracted_text = extracted_text.strip()
            
            logger.info(f"Cleaned text (first 500 chars): {extracted_text[:500]}")
            
            data = json.loads(extracted_text)
            
            logger.info(f"Successfully parsed JSON with keys: {list(data.keys())}")
            
            medical_data = MedicalData(
                patient_name=data.get('patient_name'),
                date_of_birth=data.get('date_of_birth'),
                diagnoses=data.get('diagnoses', []),
                medications=data.get('medications', []),
                lab_values=data.get('lab_values', {}),
                procedures=data.get('procedures', []),
                allergies=data.get('allergies', []),
                vital_signs=data.get('vital_signs', {}),
                notes=data.get('notes')
            )
            
            return medical_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extraction result as JSON: {e}")
            logger.error(f"Full extracted text:\n{extracted_text}")
            return None
        except Exception as e:
            logger.error(f"Error parsing extraction result: {e}")
            logger.error(f"Full extracted text:\n{extracted_text}")
            return None
