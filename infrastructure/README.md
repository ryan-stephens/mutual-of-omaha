# MedExtract Infrastructure (AWS CDK)

Production-grade Infrastructure as Code for the MedExtract MLOps platform using AWS CDK (Python).

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                  AWS Cloud Resources                  │
├──────────────────────────────────────────────────────┤
│                                                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐     │
│  │     S3     │  │  DynamoDB  │  │  DynamoDB  │     │
│  │ Documents  │  │  Results   │  │Experiments │     │
│  └────────────┘  └────────────┘  └────────────┘     │
│         │              │                │             │
│         └──────────────┴────────────────┘             │
│                        │                              │
│                   ┌────▼────┐                         │
│                   │   IAM   │                         │
│                   │  Role   │                         │
│                   └────┬────┘                         │
│                        │                              │
│                   ┌────▼────┐                         │
│                   │ Lambda  │──▶ AWS Bedrock          │
│                   │Function │                         │
│                   └────┬────┘                         │
│                        │                              │
│                   ┌────▼────┐                         │
│                   │CloudWatch                         │
│                   │ + SNS   │                         │
│                   └─────────┘                         │
└──────────────────────────────────────────────────────┘
```

## Resources Created

### Storage
- **S3 Bucket**: Document storage with versioning, lifecycle policies, encryption
  - Automatic transition to Infrequent Access after 30 days
  - Automatic deletion based on environment (30/90/365 days)
  - CORS configured for frontend uploads

### Databases
- **Results Table** (DynamoDB): Extraction results with GSIs
  - Primary Key: `document_id`
  - GSI: `UploadedAtIndex` - Query by upload time
  - GSI: `PromptVersionIndex` - Query by prompt version (MLOps)
  - Point-in-time recovery (staging/prod)
  - DynamoDB Streams enabled

- **Experiments Table** (DynamoDB): A/B test experiments
  - Primary Key: `experiment_id`
  - GSI: `StatusIndex` - Query by status
  - Tracks experiment lifecycle and results

### Security
- **IAM Role**: Least-privilege execution role for Lambda
  - S3 read/write to specific bucket
  - DynamoDB read/write to specific tables
  - Bedrock InvokeModel for Claude models only
  - CloudWatch Logs

### Monitoring (Staging/Prod)
- **CloudWatch Alarms**: 
  - DynamoDB capacity utilization
  - S3 bucket size (cost control)
- **SNS Topic**: Alert notifications

## Environment Configurations

### Development (`dev`)
- **Billing**: Pay-per-request (on-demand)
- **Lifecycle**: 30 days
- **Protection**: None (destroyable)
- **Memory**: 512 MB
- **Alarms**: Disabled

### Staging (`staging`)
- **Billing**: Pay-per-request
- **Lifecycle**: 90 days
- **Protection**: Enabled (retain on delete)
- **Memory**: 1024 MB
- **Alarms**: Enabled

### Production (`prod`)
- **Billing**: Provisioned (10 RCU / 5 WCU)
- **Lifecycle**: 365 days
- **Protection**: Enabled with backups
- **Memory**: 2048 MB
- **Alarms**: Enabled
- **Backups**: Point-in-time recovery

## Prerequisites

```bash
# Install AWS CDK
npm install -g aws-cdk

# Install Python dependencies
cd infrastructure
pip install -r requirements.txt

# Configure AWS credentials
aws configure
```

## Deployment Commands

### Bootstrap (First time only)
```bash
cdk bootstrap aws://<ACCOUNT_ID>/us-east-1
```

### Deploy to Development
```bash
cdk deploy -c env=dev
```

### Deploy to Staging
```bash
cdk deploy -c env=staging
```

### Deploy to Production
```bash
cdk deploy -c env=prod --require-approval broadening
```

### View Planned Changes (Diff)
```bash
cdk diff -c env=dev
```

### Synthesize CloudFormation
```bash
cdk synth -c env=prod > prod-template.yaml
```

### Destroy Stack (Dev only!)
```bash
cdk destroy -c env=dev
```

## Stack Outputs

After deployment, the following outputs are available:

```json
{
  "DocumentBucketName": "medextract-documents-dev-123456789",
  "ResultsTableName": "medextract-results-dev",
  "ExperimentsTableName": "medextract-experiments-dev",
  "LambdaRoleArn": "arn:aws:iam::123456789:role/...",
  "AlertTopicArn": "arn:aws:sns:us-east-1:123456789:..."
}
```

Use these outputs to configure your backend `.env` file:

```bash
# Get outputs as JSON
cdk deploy -c env=dev --outputs-file outputs.json

# Update backend .env
AWS_S3_BUCKET=<DocumentBucketName>
DYNAMODB_TABLE=<ResultsTableName>
```

## Cost Estimation

### Development (Pay-per-request)
- **DynamoDB**: ~$0.25 per 1M read/write requests
- **S3**: ~$0.023 per GB/month
- **Bedrock**: $0.25 per 1M input tokens, $1.25 per 1M output tokens
- **Estimated Monthly**: $5-20 for low usage

### Production (Provisioned)
- **DynamoDB**: 10 RCU + 5 WCU = ~$3.50/month
- **S3**: 100 GB = ~$2.30/month
- **Bedrock**: Usage-based
- **CloudWatch**: ~$1/month
- **Estimated Monthly**: $50-200 depending on usage

## CI/CD Integration

### GitHub Actions
The stack includes automated deployment via GitHub Actions:

```yaml
# .github/workflows/deploy.yml
- name: CDK Deploy
  run: cdk deploy --context env=${{ inputs.environment }}
```

### Manual Deployment
```bash
# Using GitHub Actions
gh workflow run deploy.yml -f environment=staging -f confirm=deploy
```

## Security Best Practices

✅ **Implemented:**
- Encryption at rest (S3, DynamoDB)
- Least-privilege IAM roles
- No public access to S3
- VPC endpoints for private connectivity (future)
- Secrets in AWS Secrets Manager (future)

⚠️ **TODO:**
- [ ] Enable AWS WAF for API Gateway
- [ ] Implement VPC for Lambda
- [ ] Add KMS customer-managed keys
- [ ] Enable S3 access logging
- [ ] Set up AWS Config rules

## Monitoring & Alerts

### CloudWatch Metrics
- **DynamoDB**: Consumed capacity, throttles
- **S3**: Bucket size, request count
- **Lambda**: Duration, errors, concurrent executions

### SNS Alerts
Subscribe to alert topic:
```bash
aws sns subscribe \
  --topic-arn <AlertTopicArn> \
  --protocol email \
  --notification-endpoint your-email@example.com
```

## Troubleshooting

### CDK Bootstrap Error
```bash
# If bootstrap fails, ensure you have permissions
aws sts get-caller-identity
cdk bootstrap --show-template > template.yaml  # Review permissions
```

### Deployment Fails
```bash
# Check CloudFormation events
aws cloudformation describe-stack-events \
  --stack-name MedExtractStack-dev

# View CDK debug output
cdk deploy --verbose
```

### Table Already Exists
```bash
# If DynamoDB table exists, update retention policy
cdk deploy --context env=dev --force
```

## Multi-Region Deployment

To deploy across regions:

```python
# app.py
regions = ["us-east-1", "us-west-2"]
for region in regions:
    MedExtractStack(
        app,
        f"MedExtractStack-{env_name}-{region}",
        env=Environment(account=account, region=region),
        env_name=env_name,
        config=env_config[env_name],
    )
```

## Interview Talking Points

> **"I built production infrastructure using AWS CDK with environment-specific configurations for dev, staging, and prod. The stack includes S3 with lifecycle policies, DynamoDB with global secondary indexes for MLOps queries, least-privilege IAM roles, and CloudWatch monitoring with SNS alerts. I implemented cost optimization through automatic tier transitions and configurable retention policies. The infrastructure is fully codified, version-controlled, and deployed via CI/CD pipelines."**

### Technical Depth
- Multi-environment support (dev/staging/prod)
- Cost optimization (lifecycle policies, provisioned vs on-demand)
- Security (encryption, IAM least-privilege, no public access)
- Monitoring (CloudWatch alarms, SNS alerts)
- MLOps-specific indexes (prompt version tracking)

### Production Readiness
- Deletion protection in prod
- Point-in-time recovery
- DynamoDB Streams for analytics
- Automated deployments
- CloudFormation outputs for automation

## References

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [S3 Lifecycle Policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
