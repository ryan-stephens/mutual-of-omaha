# Interview Presentation Guide: Medical Document Intelligence Platform

## Executive Summary (30 seconds)
*"I built a serverless MLOps platform that extracts structured medical data from unstructured documents using AWS Bedrock's Claude 3 model. The system handles document upload, AI-powered extraction, and provides analytics dashboards - all deployed on AWS Lambda with Infrastructure as Code."*

---

## Architecture Overview (2 minutes)

### System Components
```
┌─────────────┐
│   Frontend  │ React + TypeScript + Vite
│  (Localhost)│ TailwindCSS + shadcn/ui
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────────────────────────────┐
│     AWS API Gateway (REST API)          │
│  - CORS enabled                         │
│  - Request validation                   │
│  - Throttling & rate limiting           │
└──────┬──────────────────────────────────┘
       │
       ├──► Lambda: Upload Handler
       │    ├─► S3: Document Storage
       │    └─► DynamoDB: Metadata
       │
       ├──► Lambda: Extract Handler
       │    ├─► S3: Retrieve document
       │    ├─► Bedrock: Claude 3 extraction
       │    └─► DynamoDB: Save results
       │
       ├──► Lambda: Metrics Handler
       │    └─► DynamoDB: Aggregate stats
       │
       └──► Lambda: Experiments Handler
            └─► DynamoDB: A/B test tracking
```

### Technology Stack
- **Frontend:** React 18, TypeScript, Vite, TailwindCSS, shadcn/ui
- **Backend:** Python 3.11, FastAPI (local), AWS Lambda (production)
- **Infrastructure:** AWS CDK (TypeScript), CloudFormation
- **AI/ML:** AWS Bedrock (Claude 3 Sonnet)
- **Storage:** S3 (documents), DynamoDB (metadata & results)
- **Monitoring:** CloudWatch Logs, X-Ray tracing, Custom metrics

---

## Key Features & Design Decisions

### 1. Hybrid Architecture (Local + Serverless)
**Decision:** Support both local FastAPI and AWS Lambda deployment
**Rationale:**
- Fast local development iteration
- Production serverless scalability
- Cost-effective (pay-per-use)
- No server management

**Implementation:**
- Shared business logic in `app/services/`
- Lambda handlers in `lambda/handlers/`
- Environment-aware configuration
- Docker bundling for Lambda dependencies

### 2. Infrastructure as Code with CDK
**Decision:** Use AWS CDK instead of manual console configuration
**Rationale:**
- Version-controlled infrastructure
- Reproducible deployments
- Type-safe resource definitions
- Easy environment management (dev/staging/prod)

**Key CDK Features:**
```python
# Automatic IAM role creation with least-privilege
lambda_role = iam.Role(
    self, "LambdaExecutionRole",
    assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
    managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name(
            "service-role/AWSLambdaBasicExecutionRole"
        )
    ]
)

# Grant specific S3/DynamoDB permissions
document_bucket.grant_read_write(lambda_function)
results_table.grant_read_write_data(lambda_function)
```

### 3. Serverless MLOps Pipeline
**Decision:** Use AWS Bedrock instead of self-hosted models
**Rationale:**
- No model hosting/scaling complexity
- Access to latest Claude models
- Pay-per-token pricing
- Built-in security & compliance

**Extraction Flow:**
1. User uploads document → S3
2. Lambda triggers Bedrock API
3. Claude extracts structured data
4. Results saved to DynamoDB
5. Frontend displays formatted output

### 4. Prompt Version Management
**Decision:** Support multiple prompt versions for A/B testing
**Rationale:**
- Iterate on extraction quality
- Compare model performance
- Track metrics per version
- Enable experimentation

**Implementation:**
- Prompt files in `backend/prompts/v*.txt`
- Version selector in UI
- Metrics tracked per version
- DynamoDB stores version metadata

---

## Production Readiness Discussion

### What's Production-Ready ✅
1. **Serverless auto-scaling** - Handles traffic spikes automatically
2. **Infrastructure as Code** - Reproducible, version-controlled deployments
3. **Managed services** - No server patching, high availability built-in
4. **CORS configuration** - Secure cross-origin requests
5. **IAM least-privilege** - Minimal permissions per Lambda
6. **CloudWatch integration** - Automatic logging and monitoring
7. **X-Ray tracing enabled** - Distributed tracing ready

### Production Gaps & Solutions 🔧

#### 1. Error Handling & Resilience
**Current:** Basic try/catch, no retries
**Production Need:**
```python
from botocore.config import Config

# Exponential backoff with jitter
config = Config(
    retries={'max_attempts': 3, 'mode': 'adaptive'},
    connect_timeout=5,
    read_timeout=30
)
s3_client = boto3.client('s3', config=config)
```

#### 2. Observability
**Current:** Basic logging
**Production Need:**
- Structured JSON logs with correlation IDs
- Custom CloudWatch metrics (extraction time, success rate)
- CloudWatch dashboards for key metrics
- Alarms for error rate thresholds

```python
import json
from aws_lambda_powertools import Logger, Metrics, Tracer

logger = Logger(service="medextract")
metrics = Metrics(namespace="MedExtract")
tracer = Tracer(service="medextract")

@tracer.capture_method
def extract_document(document_id):
    logger.info("Starting extraction", extra={"document_id": document_id})
    metrics.add_metric(name="ExtractionStarted", unit="Count", value=1)
    # ... extraction logic
```

#### 3. Security Hardening
**Current:** Basic IAM roles
**Production Need:**
- S3 bucket encryption (SSE-S3 or KMS)
- DynamoDB encryption at rest
- VPC endpoints for private AWS access
- Secrets Manager for sensitive config
- API Gateway request validation

```python
# CDK: Enable encryption
document_bucket = s3.Bucket(
    self, "DocumentBucket",
    encryption=s3.BucketEncryption.S3_MANAGED,
    block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
    versioning=True,
    lifecycle_rules=[
        s3.LifecycleRule(
            expiration=Duration.days(90),  # Compliance retention
            transitions=[
                s3.Transition(
                    storage_class=s3.StorageClass.GLACIER,
                    transition_after=Duration.days(30)
                )
            ]
        )
    ]
)
```

#### 4. Testing Strategy
**Current:** Manual testing
**Production Need:**
- Unit tests with mocked AWS (moto library)
- Integration tests with LocalStack
- End-to-end tests in staging
- Load testing for performance validation

```python
# Example unit test
from moto import mock_s3, mock_dynamodb
import pytest

@mock_s3
@mock_dynamodb
def test_upload_handler():
    # Setup mock AWS resources
    s3 = boto3.client('s3')
    s3.create_bucket(Bucket='test-bucket')
    
    # Test handler
    event = {"body": json.dumps({"filename": "test.txt", "content": "..."})}
    response = upload_handler(event, None)
    
    assert response['statusCode'] == 200
```

#### 5. CI/CD Pipeline
**Current:** Manual CDK deployments
**Production Need:**
```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest tests/
      
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: CDK Deploy
        run: |
          cd infrastructure
          cdk deploy --require-approval never
```

---

## Key Metrics & Performance

### Current Performance
- **Upload latency:** ~200ms (S3 direct upload)
- **Extraction time:** 3-8 seconds (Bedrock API call)
- **Cold start:** ~1.5s (Lambda with bundled dependencies)
- **Warm invocation:** ~2ms (Lambda execution)

### Cost Optimization
- **Lambda:** Pay per 100ms execution (~$0.0000002 per request)
- **DynamoDB:** On-demand billing (pay per read/write)
- **S3:** Standard storage (~$0.023/GB/month)
- **Bedrock:** Pay per token (~$0.003 per 1K input tokens)

**Estimated monthly cost for 10K documents:**
- Lambda: $2
- DynamoDB: $5
- S3: $10
- Bedrock: $30
- **Total: ~$47/month**

---

## Interview Questions & Answers

### Q: "Why serverless instead of containers?"
**A:** "For this use case, serverless provides several advantages:
1. **Auto-scaling:** Lambda scales from 0 to 1000s of concurrent executions automatically
2. **Cost:** Pay only for actual execution time, not idle servers
3. **Ops overhead:** No server patching, no capacity planning
4. **Development speed:** Focus on business logic, not infrastructure

However, I'd consider containers (ECS/EKS) if:
- We needed long-running processes (>15 min Lambda limit)
- We had complex dependencies requiring custom runtimes
- We needed persistent connections (WebSockets, streaming)
- Cost at scale favored reserved capacity"

### Q: "How do you handle Bedrock API failures?"
**A:** "Multi-layered approach:
1. **Retry logic:** Exponential backoff with jitter (3 attempts)
2. **Circuit breaker:** Stop calling Bedrock if error rate > 50%
3. **Fallback:** Queue failed extractions for manual review
4. **Monitoring:** CloudWatch alarms on high error rates
5. **Dead letter queue:** Capture failed events for replay

Example implementation:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_bedrock(document_content):
    return bedrock_client.invoke_model(...)
```"

### Q: "How would you ensure HIPAA compliance?"
**A:** "Medical data requires strict security controls:
1. **Encryption:**
   - At rest: S3/DynamoDB KMS encryption
   - In transit: TLS 1.2+ only
2. **Access Control:**
   - IAM least-privilege roles
   - VPC endpoints (no public internet)
   - CloudTrail audit logging
3. **Data Retention:**
   - Automated deletion after retention period
   - S3 Object Lock for immutability
4. **AWS BAA:**
   - Sign Business Associate Agreement with AWS
   - Use HIPAA-eligible services only
5. **Monitoring:**
   - GuardDuty for threat detection
   - Config for compliance checks
   - Security Hub for centralized view"

### Q: "How do you test Lambda functions locally?"
**A:** "Multiple approaches:
1. **LocalStack:** Emulates AWS services locally
2. **SAM CLI:** `sam local invoke` with test events
3. **Unit tests:** Mock AWS with `moto` library
4. **Integration tests:** Deploy to dev environment
5. **Docker:** Run Lambda container images locally

My preference: Unit tests with moto for fast feedback, then integration tests in dev AWS account before production."

### Q: "What's your deployment strategy?"
**A:** "For production, I'd implement:
1. **Blue/Green Deployment:**
   - Deploy new version alongside old
   - Gradually shift traffic (10% → 50% → 100%)
   - Automatic rollback on errors
   
2. **Canary Releases:**
   - Lambda aliases with weighted routing
   - Monitor metrics during rollout
   - Abort if error rate increases

3. **Feature Flags:**
   - Toggle new features without deployment
   - A/B test in production
   - Quick rollback by disabling flag

CDK supports this with:
```python
lambda_.Alias(
    self, "ProdAlias",
    alias_name="prod",
    version=new_version,
    provisioned_concurrent_executions=10,
    # Canary deployment
    deployment_config=lambda_.LambdaDeploymentConfig.CANARY_10_PERCENT_5_MINUTES
)
```"

---

## Demo Script (5 minutes)

### 1. Show Architecture Diagram (30 sec)
"This is a serverless MLOps platform for medical document intelligence..."

### 2. Live Demo (2 min)
1. Upload sample medical note
2. Show real-time extraction with Bedrock
3. Display structured results
4. Show metrics dashboard

### 3. Code Walkthrough (2 min)
- CDK infrastructure definition
- Lambda handler with error handling
- Bedrock API integration
- Frontend React components

### 4. Production Discussion (30 sec)
"While this works, for production I'd add [point to PRODUCTION_READINESS.md]:
- Comprehensive error handling
- Structured logging & metrics
- Security hardening (encryption, VPC)
- Automated testing & CI/CD"

---

## Conclusion

**What This Demonstrates:**
✅ Full-stack development (React + Python)
✅ Cloud architecture (AWS serverless)
✅ Infrastructure as Code (CDK)
✅ AI/ML integration (Bedrock)
✅ Production thinking (identified gaps)
✅ System design skills (scalability, security)

**Key Takeaway:**
*"I can build functional MVPs quickly, but I also understand what it takes to make them production-ready. I know the difference between 'it works' and 'it's enterprise-grade'."*
