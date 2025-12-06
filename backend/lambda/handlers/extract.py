"""
Lambda handler for ML extraction operations via AWS Bedrock
"""

import logging
import time
from datetime import datetime
import sys
import os
from pathlib import Path

sys.path.insert(0, "/opt/python")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    create_response,
    create_error_response,
    parse_event_body,
    get_path_parameter,
)
from app.models.schemas import DocumentStatus
import boto3
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize AWS clients directly
s3_client = boto3.client("s3")
dynamodb_resource = boto3.resource("dynamodb")
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

# Get environment variables
S3_BUCKET = os.environ.get("S3_BUCKET")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE")


def load_prompt(version: str) -> str:
    """
    Load prompt from file based on version

    Args:
        version: Prompt version (e.g., 'v1.0.0', 'v2.0.0')

    Returns:
        Prompt content as string
    """
    # Get the prompts directory relative to this file
    handler_dir = Path(__file__).parent
    prompts_dir = handler_dir.parent.parent / "prompts"
    prompt_file = prompts_dir / f"{version}.txt"

    logger.info(f"Loading prompt from: {prompt_file}")

    if not prompt_file.exists():
        logger.warning(f"Prompt file not found: {prompt_file}, falling back to v2.0.0")
        prompt_file = prompts_dir / "v2.0.0.txt"

    try:
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading prompt file: {e}")
        # Return default v2.0.0 prompt as fallback
        return """You are a specialized medical information extraction system designed for underwriting workflows. Your objective is to extract structured, normalized data from medical documents with maximum accuracy and completeness.

Extract and structure the following information as JSON:

{
  "patient_name": "Full patient name",
  "date_of_birth": "DOB in YYYY-MM-DD format",
  "diagnoses": [
    {
      "condition": "Standardized diagnosis name",
      "icd_code": "ICD-10 code if available",
      "severity": "mild/moderate/severe if stated",
      "date_diagnosed": "Date if available"
    }
  ],
  "medications": [
    {
      "name": "Medication name (generic preferred)",
      "dosage": "Strength and unit",
      "frequency": "How often taken",
      "route": "Administration route",
      "indication": "Reason for medication if stated"
    }
  ],
  "lab_values": {
    "test_name": {
      "value": "Result with units",
      "reference_range": "Normal range if provided",
      "date": "Test date if available",
      "flag": "H/L/Normal"
    }
  },
  "procedures": [
    {
      "name": "Procedure name",
      "date": "When performed",
      "outcome": "Result or status if mentioned"
    }
  ],
  "allergies": [
    {
      "allergen": "Substance name",
      "reaction": "Type of reaction",
      "severity": "mild/moderate/severe/life-threatening"
    }
  ],
  "vital_signs": {
    "vital_name": {
      "value": "Measurement with units",
      "date": "When measured"
    }
  },
  "risk_factors": ["Relevant risk factors for underwriting"],
  "notes": "Additional clinically significant information"
}

Extraction Protocol:
1. ACCURACY: Extract only explicitly stated information. Never infer or assume.
2. NORMALIZATION: Standardize all medical terminology:
   - T2DM → Type 2 Diabetes Mellitus
   - HTN → Hypertension
   - CAD → Coronary Artery Disease
   - COPD → Chronic Obstructive Pulmonary Disease
   - CHF → Congestive Heart Failure
3. COMPLETENESS: Include all available details (dates, units, ranges, severity)
4. STRUCTURE: Use nested objects for complex data
5. CONSISTENCY: Maintain consistent formatting throughout
6. VALIDATION: Ensure all numeric values include units
7. RISK ASSESSMENT: Identify underwriting-relevant risk factors

Medical Document:
{document_content}

Return ONLY the JSON object. No markdown, no explanations, no additional commentary."""


def handler(event, context):
    """
    Process extraction requests via AWS Bedrock

    Expects path parameter: document_id
    Optional body: prompt_version
    """
    try:
        document_id = get_path_parameter(event, "document_id")

        if not document_id:
            return create_error_response(400, "Missing document_id path parameter")

        logger.info(f"Processing extraction for document: {document_id}")

        body = parse_event_body(event)
        prompt_version = body.get("prompt_version", "v2.0.0")

        # Get document metadata from DynamoDB
        table = dynamodb_resource.Table(DYNAMODB_TABLE)
        response = table.get_item(Key={"document_id": document_id})

        if "Item" not in response:
            return create_error_response(404, f"Document not found: {document_id}")

        result = response["Item"]
        s3_key = result.get("s3_key")
        if not s3_key:
            return create_error_response(400, "Document has no S3 key")

        # Update status to processing
        table.update_item(
            Key={"document_id": document_id},
            UpdateExpression="SET #status = :status",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":status": DocumentStatus.PROCESSING.value},
        )

        start_time = time.time()

        try:
            # Get document content from S3
            s3_response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
            document_content = s3_response["Body"].read().decode("utf-8")
            logger.info(f"Retrieved document from S3: {len(document_content)} bytes")

            # Call Bedrock for extraction
            # Note: Using Claude 3 Haiku (not 3.5) as 3.5 requires inference profiles
            model_id = "anthropic.claude-3-haiku-20240307-v1:0"

            # Load prompt template based on version
            logger.info(f"Using prompt version: {prompt_version}")
            prompt_template = load_prompt(prompt_version)

            # Insert document content into prompt
            prompt = prompt_template.replace("{document_content}", document_content)

            bedrock_request = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,  # Increased for comprehensive extraction
                "messages": [{"role": "user", "content": prompt}],
            }

            bedrock_response = bedrock_runtime.invoke_model(
                modelId=model_id, body=json.dumps(bedrock_request)
            )

            response_body = json.loads(bedrock_response["body"].read())
            extracted_text = response_body["content"][0]["text"]
            
            # Extract token usage for metrics
            token_usage = {
                "input_tokens": response_body.get("usage", {}).get("input_tokens", 0),
                "output_tokens": response_body.get("usage", {}).get("output_tokens", 0),
            }

            # Try to parse as JSON
            try:
                medical_data = json.loads(extracted_text)
            except:
                medical_data = {"raw_text": extracted_text}

            processing_time_ms = int((time.time() - start_time) * 1000)

            # Save results to DynamoDB
            table.update_item(
                Key={"document_id": document_id},
                UpdateExpression="SET medical_data = :data, #status = :status, model_id = :model, prompt_version = :version, processing_time_ms = :time, extracted_at = :timestamp, token_usage = :tokens",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":data": medical_data,
                    ":status": DocumentStatus.COMPLETED.value,
                    ":model": model_id,
                    ":version": prompt_version,
                    ":time": processing_time_ms,
                    ":timestamp": datetime.utcnow().isoformat(),
                    ":tokens": token_usage,
                },
            )

            return create_response(
                200,
                {
                    "document_id": document_id,
                    "status": DocumentStatus.COMPLETED.value,
                    "medical_data": medical_data,
                    "processing_time_ms": processing_time_ms,
                    "model_id": model_id,
                    "prompt_version": prompt_version,
                    "token_usage": token_usage,
                    "extracted_at": datetime.utcnow().isoformat(),
                },
            )

        except Exception as extraction_error:
            logger.error(
                f"Extraction failed for {document_id}: {extraction_error}",
                exc_info=True,
            )

            processing_time_ms = int((time.time() - start_time) * 1000)

            # Save error to DynamoDB
            table.update_item(
                Key={"document_id": document_id},
                UpdateExpression="SET #status = :status, error_message = :error, processing_time_ms = :time",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":status": DocumentStatus.FAILED.value,
                    ":error": str(extraction_error),
                    ":time": processing_time_ms,
                },
            )

            return create_error_response(
                500, f"Extraction failed: {str(extraction_error)}"
            )

    except Exception as e:
        logger.error(f"Handler error: {e}", exc_info=True)
        return create_error_response(500, f"Processing failed: {str(e)}")
