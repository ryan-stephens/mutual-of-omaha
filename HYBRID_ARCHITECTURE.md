# MedExtract Hybrid Architecture Guide

## 🎯 Quick Overview

MedExtract now supports **Option C: Hybrid Approach** - the best of both worlds!

```
┌─────────────────────────────────────────────────────────┐
│              HYBRID ARCHITECTURE                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Development:  FastAPI (localhost:8000)                 │
│  Production:   AWS Lambda + API Gateway                 │
│                                                          │
│  Same codebase, different deployment targets!           │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
mutual-of-omaha/
├── backend/
│   ├── app/                    # FastAPI application (local dev)
│   │   ├── main.py            # FastAPI entry point
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic (shared!)
│   │   └── models/            # Data models
│   │
│   ├── lambda/                # Lambda deployment (production)
│   │   ├── handlers/          # Lambda function handlers
│   │   │   ├── upload.py     # ✅ Implemented
│   │   │   ├── extract.py    # ✅ Implemented
│   │   │   ├── metrics.py    # ✅ Implemented
│   │   │   └── experiment.py # ✅ Implemented
│   │   └── utils.py          # ✅ Shared Lambda utilities
│   │
│   └── requirements.txt       # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── config.ts          # ✅ Environment-aware config
│   │   └── generated/
│   │       └── client.gen.ts  # ✅ Updated for env vars
│   │
│   ├── .env.local             # ✅ Local dev config
│   └── .env.production        # ✅ Production config
│
├── infrastructure/
│   └── stacks/
│       └── medextract_stack.py # ✅ CDK infrastructure
│
└── docs/
    ├── DEPLOYMENT.md          # ✅ Full deployment guide
    └── LAMBDA_ARCHITECTURE.md # Architecture details
```

---

## 🚀 How It Works

### Local Development (Current Default)

**Backend:**
```powershell
cd backend
uvicorn app.main:app --reload
# Runs at http://localhost:8000
```

**Frontend:**
```powershell
cd frontend
npm run dev
# Uses .env.local → VITE_API_BASE_URL=http://localhost:8000
```

**Architecture:**
```
React Frontend → FastAPI (localhost:8000) → AWS Services
                                             ├─ S3
                                             ├─ DynamoDB
                                             └─ Bedrock
```

### Production Deployment

**Deploy Backend:**
```powershell
cd infrastructure
cdk deploy -c env=prod --all
# Deploys Lambda functions + API Gateway
```

**Deploy Frontend:**
```powershell
cd frontend
npm run build
vercel --prod
# Uses .env.production → VITE_API_BASE_URL=https://api-gateway-url
```

**Architecture:**
```
React Frontend → API Gateway → Lambda Functions → AWS Services
                                ├─ upload.py      ├─ S3
                                ├─ extract.py     ├─ DynamoDB
                                ├─ metrics.py     └─ Bedrock
                                └─ experiment.py
```

---

## 🔑 Key Components

### 1. Shared Business Logic

**Location:** `backend/app/services/`

These services are used by **BOTH** FastAPI and Lambda:
- ✅ `s3_service.py` - Document storage
- ✅ `dynamodb_service.py` - Data persistence
- ✅ `bedrock_service.py` - ML extraction
- ✅ `metrics_service.py` - MLOps metrics
- ✅ `experiment_service.py` - A/B testing

**Why this works:**
- Lambda handlers import from `app.services`
- FastAPI routers import from `app.services`
- **Same code, zero duplication!**

### 2. Lambda Handlers (NEW)

**Location:** `backend/lambda/handlers/`

Thin wrappers that:
1. Parse API Gateway events
2. Call shared services
3. Return API Gateway responses

**Example:**
```python
# backend/lambda/handlers/upload.py
from app.services.s3_service import S3Service  # Shared!
from lambda_utils import create_response

s3_service = S3Service()

def handler(event, context):
    # Parse API Gateway event
    body = parse_event_body(event)
    
    # Use shared service
    document_id, s3_key = s3_service.upload_file(content, filename)
    
    # Return API Gateway response
    return create_response(200, {'document_id': document_id})
```

### 3. Environment-Based Configuration

**Frontend:**
```typescript
// src/config.ts
export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
};

// src/generated/client.gen.ts
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const client = createClient(createConfig({ baseUrl: apiBaseUrl }));
```

**Environment Files:**
- `.env.local` → `VITE_API_BASE_URL=http://localhost:8000` (dev)
- `.env.production` → `VITE_API_BASE_URL=https://your-api-gateway-url` (prod)

---

## 🎬 Quick Start Commands

### Local Development (Default)

```powershell
# Terminal 1: Backend
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

Visit: `http://localhost:5174`

### Deploy to AWS Lambda

```powershell
# 1. Deploy infrastructure
cd infrastructure
cdk deploy -c env=dev --all

# 2. Copy API Gateway URL from output
# Example: https://abc123.execute-api.us-east-1.amazonaws.com/prod

# 3. Update frontend config
cd ../frontend
# Edit .env.production with your API Gateway URL

# 4. Deploy frontend
npm run build
vercel --prod
```

---

## 🔄 Development Workflow

### Making Changes

**1. Develop locally (FastAPI):**
```powershell
# Make changes to backend/app/services/
# Test with FastAPI server
uvicorn app.main:app --reload
```

**2. Test changes work:**
```powershell
# Frontend automatically uses local backend
npm run dev
```

**3. Deploy to Lambda when ready:**
```powershell
cd infrastructure
cdk deploy -c env=dev --all
```

**Why this works:**
- Lambda handlers use the **same services** you just tested locally
- No code changes needed between local and Lambda
- Confidence that it will work in production!

---

## 📊 Comparison: Local vs Lambda

| Feature | Local (FastAPI) | Production (Lambda) |
|---------|----------------|---------------------|
| **Startup** | `uvicorn app.main:app` | Automatic (API Gateway) |
| **Cost** | $0 (runs on your machine) | ~$5-10/month (pay per use) |
| **Scaling** | Single process | Auto-scales to 1000s |
| **Deployment** | No deployment needed | `cdk deploy` |
| **Debugging** | Easy (print statements) | CloudWatch Logs |
| **Cold Starts** | None | ~600ms (1% of requests) |
| **Best For** | Development, testing | Production, demos |

---

## 🎯 When to Use Each

### Use Local FastAPI When:
- ✅ Developing new features
- ✅ Testing changes quickly
- ✅ Debugging issues
- ✅ Running unit tests
- ✅ Cost is a concern

### Use Lambda When:
- ✅ Deploying for production
- ✅ Sharing with others (demo)
- ✅ Need auto-scaling
- ✅ Want serverless benefits
- ✅ Interview presentation

---

## 🚨 Important Notes

### Lambda Handler Imports

Lambda handlers need special path configuration:

```python
import sys
import os
sys.path.insert(0, '/opt/python')  # Lambda layer dependencies
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))  # App code

# Now you can import shared services
from app.services.s3_service import S3Service
```

### Environment Variables

**Lambda functions automatically receive:**
- `DYNAMODB_TABLE` - Results table name
- `EXPERIMENTS_TABLE` - Experiments table name
- `S3_BUCKET` - Document bucket name
- `ENVIRONMENT` - dev/staging/prod
- `AWS_REGION` - Provided by Lambda runtime (don't set manually!)

**Local FastAPI uses `.env` file:**
```env
AWS_REGION=us-east-1
S3_BUCKET_NAME=medextract-documents
DYNAMODB_TABLE_NAME=medextract-results
```

---

## 📚 Documentation

- **`docs/DEPLOYMENT.md`** - Complete deployment guide
- **`docs/LAMBDA_ARCHITECTURE.md`** - Lambda architecture details
- **`backend/README.md`** - Backend setup
- **`frontend/README.md`** - Frontend setup

---

## ✅ What You Have Now

✅ **Fully functional local development** (FastAPI)  
✅ **Production-ready Lambda handlers** (4 functions implemented)  
✅ **Shared business logic** (no code duplication)  
✅ **Environment-based frontend** (auto-switches API URLs)  
✅ **CDK infrastructure** (ready to deploy)  
✅ **Comprehensive documentation** (deployment guide)  

---

## 🎉 Next Steps

1. **Continue developing locally** - Use FastAPI for fast iteration
2. **Deploy when ready** - Use Lambda for production/demos
3. **Monitor in CloudWatch** - Track Lambda performance
4. **Optimize costs** - Right-size Lambda memory based on metrics

---

**You now have the best of both worlds: fast local development + scalable serverless production!** 🚀

---

**Last Updated:** 2025-12-05  
**Architecture:** Hybrid (FastAPI + Lambda)  
**Status:** ✅ Fully Implemented
