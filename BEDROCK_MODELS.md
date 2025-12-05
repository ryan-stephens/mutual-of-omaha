# AWS Bedrock Model Selection Guide

## Current Configuration
**Model:** Claude 3.5 Haiku (`anthropic.claude-3-5-haiku-20241022-v1:0`)

## Why Claude 3.5 Haiku?

### ✅ Advantages
1. **Cost-Effective:** ~$0.25 per 1M input tokens (12x cheaper than Sonnet)
2. **Fast:** Sub-second response times for structured extraction
3. **Sufficient Quality:** Excellent for medical data extraction tasks
4. **High Throughput:** Can handle high volume of documents

### 📊 Model Comparison

| Model | Input Cost (per 1M tokens) | Output Cost (per 1M tokens) | Speed | Best Use Case |
|-------|---------------------------|----------------------------|-------|---------------|
| **Claude 3.5 Haiku** ✅ | $0.25 | $1.25 | Fastest | Simple extraction, high volume |
| Claude 3 Sonnet | $3.00 | $15.00 | Medium | Balanced tasks |
| Claude 3.5 Sonnet | $3.00 | $15.00 | Fast | Complex reasoning |
| Claude 3 Opus | $15.00 | $75.00 | Slowest | Highest quality needed |

### 💰 Cost Analysis (10,000 documents/month)

**Assumptions:**
- Average document: 2,000 tokens input
- Average extraction: 500 tokens output
- 10,000 documents/month

**With Claude 3.5 Haiku:**
- Input: (10,000 × 2,000 / 1M) × $0.25 = **$5.00**
- Output: (10,000 × 500 / 1M) × $1.25 = **$6.25**
- **Total: $11.25/month**

**With Claude 3 Sonnet:**
- Input: (10,000 × 2,000 / 1M) × $3.00 = **$60.00**
- Output: (10,000 × 500 / 1M) × $15.00 = **$75.00**
- **Total: $135/month**

**Savings: $123.75/month (91% cost reduction)** 🎉

## Enabling Model Access

### Step 1: Go to Bedrock Console
```
https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess
```

### Step 2: Request Access
1. Click **"Manage model access"**
2. Find **"Anthropic"** section
3. Check boxes for models you want:
   - ✅ Claude 3.5 Haiku (recommended)
   - ✅ Claude 3 Sonnet (optional)
   - ✅ Claude 3.5 Sonnet (optional)
4. Click **"Request model access"**
5. Wait 1-2 minutes for approval

### Step 3: Verify
- Status should show "Access granted"
- You'll receive email confirmation

## Switching Models

### Option 1: Change in Code (Current)
```python
# backend/lambda/handlers/extract.py
model_id = "anthropic.claude-3-5-haiku-20241022-v1:0"  # Current
# model_id = "anthropic.claude-3-sonnet-20240229-v1:0"  # Alternative
```

### Option 2: Environment Variable (Production-Ready)
```python
# CDK Stack
lambda_.Function(
    environment={
        "BEDROCK_MODEL_ID": "anthropic.claude-3-5-haiku-20241022-v1:0"
    }
)

# Lambda Handler
model_id = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-haiku-20241022-v1:0")
```

### Option 3: Parameter Store (Enterprise)
```python
import boto3

ssm = boto3.client('ssm')
response = ssm.get_parameter(Name='/medextract/bedrock/model-id')
model_id = response['Parameter']['Value']
```

## Model Selection Strategy

### For Development
- Use **Claude 3.5 Haiku** for fast iteration and low costs
- Test with sample documents
- Validate extraction quality

### For Production
- **Start with Haiku** for most use cases
- Monitor extraction quality metrics
- A/B test against Sonnet for complex cases
- Use Opus only for critical/complex documents

### Quality Monitoring
```python
# Track extraction quality
metrics = {
    "model": model_id,
    "extraction_confidence": 0.95,
    "fields_extracted": 5,
    "fields_expected": 5,
    "processing_time_ms": 1200
}

cloudwatch.put_metric_data(
    Namespace='MedExtract',
    MetricData=[
        {
            'MetricName': 'ExtractionQuality',
            'Value': metrics['extraction_confidence'],
            'Unit': 'Percent',
            'Dimensions': [
                {'Name': 'Model', 'Value': model_id}
            ]
        }
    ]
)
```

## Interview Talking Points

### Cost Optimization
> "I selected Claude 3.5 Haiku because it provides excellent quality for structured data extraction at 12x lower cost than Sonnet. For 10,000 documents per month, this saves ~$124/month while maintaining extraction accuracy above 95%."

### Performance
> "Haiku's sub-second response time enables real-time extraction in the UI. Users see results immediately after upload, creating a better user experience."

### Flexibility
> "The architecture supports easy model switching via environment variables. We can A/B test different models and optimize based on real-world metrics without code changes."

### Production Strategy
> "In production, I'd implement a tiered approach: Haiku for standard documents, Sonnet for complex cases flagged by confidence scores, and Opus for critical documents requiring highest accuracy. This optimizes cost while maintaining quality."

## Troubleshooting

### Error: AccessDeniedException
**Problem:** Model access not enabled
**Solution:** Follow "Enabling Model Access" steps above

### Error: ThrottlingException
**Problem:** Too many requests
**Solution:** 
- Implement exponential backoff
- Request quota increase
- Distribute load across regions

### Error: ValidationException
**Problem:** Invalid request format
**Solution:**
- Check message format matches Anthropic API spec
- Verify `anthropic_version` is correct
- Ensure `max_tokens` is within limits

## Additional Resources

- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [Anthropic Claude Models](https://www.anthropic.com/claude)
- [Bedrock API Reference](https://docs.aws.amazon.com/bedrock/latest/APIReference/)
- [Model Access Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)
