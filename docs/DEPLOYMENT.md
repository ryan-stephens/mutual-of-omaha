# MedExtract Deployment Guide

## 🎯 Overview

MedExtract supports **hybrid deployment**:
- **Local Development:** FastAPI server on `localhost:8000`
- **Production:** AWS Lambda + API Gateway serverless deployment

---

## 🏠 Local Development Setup

### Backend (FastAPI)

```powershell
# Navigate to backend
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: `http://localhost:8000`
API Docs: `http://localhost:8000/api/docs`

### Frontend (React + Vite)

```powershell
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Run development server
npm run dev
```

Frontend runs at: `http://localhost:5174`

**Environment:** Uses `.env.local` with `VITE_API_BASE_URL=http://localhost:8000`

---

## ☁️ AWS Lambda Deployment

### Prerequisites

1. **AWS CLI configured:**
   ```powershell
   aws configure
   # Enter: Access Key, Secret Key, Region (us-east-1), Output format (json)
   ```

2. **AWS CDK installed:**
   ```powershell
   npm install -g aws-cdk
   ```

3. **Python dependencies:**
   ```powershell
   cd backend
   pip install -r requirements.txt
   ```

4. **Node.js dependencies:**
   ```powershell
   cd infrastructure
   npm install
   ```

### Step 1: Bootstrap CDK (First Time Only)

```powershell
cd infrastructure
cdk bootstrap aws://YOUR_ACCOUNT_ID/us-east-1
```

Replace `YOUR_ACCOUNT_ID` with your AWS account ID (get via `aws sts get-caller-identity`).

### Step 2: Deploy Infrastructure

```powershell
cd infrastructure

# Synthesize CloudFormation template (preview)
cdk synth -c env=dev

# Deploy to AWS
cdk deploy -c env=dev --all

# For production
cdk deploy -c env=prod --all
```

**What gets deployed:**
- ✅ 4 Lambda functions (upload, extract, metrics, experiment)
- ✅ API Gateway REST API
- ✅ S3 bucket for documents
- ✅ 2 DynamoDB tables (results, experiments)
- ✅ IAM roles with least privilege
- ✅ CloudWatch log groups
- ✅ X-Ray tracing

### Step 3: Get API Gateway URL

After deployment, CDK outputs the API Gateway URL:

```
Outputs:
MedExtractStack.ApiGatewayUrl = https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
```

**Copy this URL!** You'll need it for the frontend.

### Step 4: Update Frontend Configuration

```powershell
cd frontend

# Edit .env.production
# Replace with your actual API Gateway URL
VITE_API_BASE_URL=https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
```

### Step 5: Build and Deploy Frontend

**Option A: Deploy to S3 + CloudFront (AWS)**

```powershell
cd frontend

# Build production bundle
npm run build

# Deploy to S3 (create bucket first)
aws s3 mb s3://medextract-frontend-prod
aws s3 sync dist/ s3://medextract-frontend-prod --delete

# Enable static website hosting
aws s3 website s3://medextract-frontend-prod --index-document index.html
```

**Option B: Deploy to Vercel (Recommended for Speed)**

```powershell
cd frontend

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod

# Set environment variable in Vercel dashboard:
# VITE_API_BASE_URL = https://your-api-gateway-url.amazonaws.com/prod
```

---

## 🔄 Update Deployment

### Update Backend (Lambda Functions)

```powershell
cd infrastructure
cdk deploy -c env=dev --all
```

CDK automatically:
- Packages Lambda code
- Uploads to S3
- Updates Lambda functions
- Zero downtime deployment

### Update Frontend

```powershell
cd frontend
npm run build

# If using S3
aws s3 sync dist/ s3://medextract-frontend-prod --delete

# If using Vercel
vercel --prod
```

---

## 🧪 Testing Deployment

### Test Backend (Lambda)

```powershell
# Health check
curl https://your-api-gateway-url.amazonaws.com/prod/api/health

# Upload test document
curl -X POST https://your-api-gateway-url.amazonaws.com/prod/api/upload \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.txt", "file_content": "SGVsbG8gV29ybGQ="}'
```

### Test Frontend

1. Open browser to your frontend URL
2. Upload a sample medical document
3. Process the document
4. View extraction results
5. Check CloudWatch logs for Lambda execution

---

## 📊 Monitoring

### CloudWatch Logs

```powershell
# View Lambda logs
aws logs tail /aws/lambda/medextract-upload-dev --follow
aws logs tail /aws/lambda/medextract-extract-dev --follow
```

### CloudWatch Metrics

Navigate to AWS Console → CloudWatch → Dashboards

**Key Metrics:**
- Lambda Invocations
- Lambda Duration
- Lambda Errors
- API Gateway 4XX/5XX errors
- DynamoDB Read/Write capacity

### X-Ray Tracing

Navigate to AWS Console → X-Ray → Service Map

View end-to-end request traces:
```
API Gateway → Lambda → DynamoDB
             ↓
           Bedrock
```

---

## 💰 Cost Monitoring

### Set Up Billing Alerts

```powershell
# Create SNS topic for alerts
aws sns create-topic --name billing-alerts

# Subscribe your email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:billing-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com

# Create CloudWatch alarm
aws cloudwatch put-metric-alarm \
  --alarm-name daily-cost-alert \
  --alarm-description "Alert if daily cost exceeds $5" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:billing-alerts
```

### Expected Costs

**Development (Low Usage):**
- Lambda: $0-5/month (within free tier)
- API Gateway: $0-3/month (within free tier)
- DynamoDB: $0 (within free tier)
- S3: $0-1/month
- Bedrock: $0.05-0.50/month (depends on usage)
- **Total: $5-10/month**

**Production (Moderate Usage):**
- Lambda: $10-30/month
- API Gateway: $5-15/month
- DynamoDB: $5-10/month
- S3: $2-5/month
- Bedrock: $10-50/month
- **Total: $30-110/month**

---

## 🔐 Security Best Practices

### 1. API Gateway Authentication

Add API key requirement:

```typescript
// infrastructure/stacks/medextract_stack.ts
const apiKey = api.addApiKey('ApiKey', {
  apiKeyName: 'medextract-api-key',
});

const usagePlan = api.addUsagePlan('UsagePlan', {
  throttle: {
    rateLimit: 100,
    burstLimit: 200,
  },
});

usagePlan.addApiKey(apiKey);
```

### 2. CORS Configuration

Update allowed origins in Lambda handlers:

```python
# backend/lambda/utils.py
default_headers = {
    'Access-Control-Allow-Origin': 'https://your-frontend-domain.com',  # Specific domain
    # ... other headers
}
```

### 3. Environment Variables

Never commit secrets! Use AWS Secrets Manager:

```powershell
# Store secret
aws secretsmanager create-secret \
  --name medextract/api-key \
  --secret-string "your-secret-value"

# Grant Lambda access
# (Already configured in CDK IAM role)
```

### 4. VPC Configuration (Optional for HIPAA)

For PHI compliance, deploy Lambda in VPC:

```typescript
// infrastructure/stacks/medextract_stack.ts
const vpc = new ec2.Vpc(this, 'MedExtractVpc', {
  maxAzs: 2,
});

lambda_.Function(this, 'ExtractFunction', {
  vpc: vpc,
  vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
  // ... other config
});
```

---

## 🚨 Troubleshooting

### Lambda Import Errors

**Problem:** `ModuleNotFoundError: No module named 'app'`

**Solution:** Check Lambda handler path configuration:

```python
# backend/lambda/handlers/upload.py
import sys
import os
sys.path.insert(0, '/opt/python')  # Lambda layer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))  # App code
```

### API Gateway CORS Errors

**Problem:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:** Ensure Lambda returns CORS headers:

```python
return {
    'statusCode': 200,
    'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    },
    'body': json.dumps(data)
}
```

### Lambda Timeout

**Problem:** `Task timed out after 60.00 seconds`

**Solution:** Increase timeout in CDK:

```typescript
lambda_.Function(this, 'ExtractFunction', {
  timeout: Duration.seconds(300),  // 5 minutes
  // ... other config
});
```

### DynamoDB Throttling

**Problem:** `ProvisionedThroughputExceededException`

**Solution:** Enable auto-scaling or use on-demand billing:

```typescript
const table = new dynamodb.Table(this, 'ResultsTable', {
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,  // On-demand
  // ... other config
});
```

---

## 🔄 Rollback Deployment

### Rollback Lambda Function

```powershell
# List versions
aws lambda list-versions-by-function --function-name medextract-extract-dev

# Rollback to previous version
aws lambda update-alias \
  --function-name medextract-extract-dev \
  --name prod \
  --function-version 3  # Previous version number
```

### Rollback CDK Stack

```powershell
cd infrastructure

# Destroy current deployment
cdk destroy -c env=dev --all

# Redeploy from previous commit
git checkout <previous-commit-hash>
cdk deploy -c env=dev --all
```

---

## 📚 Additional Resources

- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [AWS CDK Python Guide](https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html)
- [Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)

---

**Last Updated:** 2025-12-05  
**Author:** Ryan Stephens  
**Project:** MedExtract MLOps Platform
