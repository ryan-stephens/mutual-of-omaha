# MedExtract - Medical Document Intelligence Project

**Goal:** Build a Gen AI application that extracts structured data from unstructured medical documents using AWS Bedrock

**Timeline:** 1-2 weeks  
**Target Demo Date:** Before Mutual of Omaha interview

---

## 🎯 Project Objectives

1. **Demonstrate AWS Bedrock proficiency** - Claude 3 integration for text extraction
2. **Show full-stack capabilities** - React frontend + Python backend
3. **Prove MLOps understanding** - Versioning, monitoring, A/B testing
4. **Mirror their use case** - Structuring unstructured medical data (underwriting)
5. **Build portfolio piece** - Professional demo for interview

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend: React + TypeScript + TailwindCSS                 │
│  - File upload interface                                    │
│  - Results display (structured data)                        │
│  - Processing status tracking                               │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS
                      ↓
┌─────────────────────────────────────────────────────────────┐
│  AWS API Gateway                                            │
│  - REST API endpoints                                       │
│  - CORS configuration                                       │
│  - Request validation                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│  AWS Lambda (Python + FastAPI)                             │
│  - /upload - Accept documents                              │
│  - /process - Trigger Bedrock extraction                   │
│  - /results/:id - Retrieve structured data                 │
└──────────┬──────────────────────┬──────────────────────────┘
           │                      │
           ↓                      ↓
┌──────────────────┐   ┌─────────────────────────────────────┐
│  AWS S3          │   │  AWS Bedrock (Claude 3)             │
│  - Raw documents │   │  - Text extraction                  │
│  - Versioning    │   │  - Entity recognition               │
└──────────────────┘   │  - Structured output generation     │
                       └─────────────────┬───────────────────┘
                                         │
                                         ↓
                       ┌─────────────────────────────────────┐
                       │  DynamoDB                           │
                       │  - Extracted data storage           │
                       │  - Processing metadata              │
                       │  - Version tracking                 │
                       └─────────────────────────────────────┘
                                         │
                                         ↓
                       ┌─────────────────────────────────────┐
                       │  CloudWatch                         │
                       │  - Request logging                  │
                       │  - Performance metrics              │
                       │  - Error tracking                   │
                       └─────────────────────────────────────┘
```

---

## 📦 Tech Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Frontend** | React 18 + TypeScript | Matches job requirements |
| **Styling** | TailwindCSS | Modern, responsive UI |
| **Backend** | Python 3.11 + FastAPI | Job requirement (Python backend) |
| **AI/ML** | AWS Bedrock (Claude 3 Haiku) | Job requirement, cost-effective |
| **Document Storage** | AWS S3 | Native AWS, simple integration |
| **Database** | DynamoDB | Serverless, fast key-value lookups |
| **Compute** | AWS Lambda | Serverless, pay-per-use |
| **API** | AWS API Gateway | Standard AWS API layer |
| **IaC** | AWS CDK (TypeScript) | Job requirement (Infrastructure as Code) |
| **CI/CD** | GitHub Actions | You already know this |
| **Monitoring** | CloudWatch | AWS native observability |
| **Testing** | Pytest (backend), Playwright (E2E) | Production-quality testing |

---

## 📅 Development Phases

### **Phase 0: Setup & Prerequisites (1-2 days)**
**Status:** 🔴 Not Started

#### Tasks:
- [ ] Create AWS account (if needed) or use existing
- [ ] Request AWS Bedrock model access (Claude 3)
  - Navigate to Bedrock console → Model access → Request access
  - **Note:** Can take 1-2 business days for approval
- [ ] Install AWS CLI and configure credentials
- [ ] Set up project repository structure
- [ ] Install Python 3.11+ and Node.js 20+
- [ ] Create `.gitignore` for AWS credentials, `.env` files
- [ ] Set up GitHub repository with README

#### Deliverables:
- AWS account with Bedrock access approved
- Local development environment ready
- GitHub repo initialized

---

### **Phase 1: Backend Foundation (Days 3-4)**
**Status:** 🔴 Not Started

#### Tasks:
- [ ] Create Python virtual environment
- [ ] Install dependencies: `fastapi`, `boto3`, `python-multipart`, `pydantic`
- [ ] Set up FastAPI project structure:
  ```
  backend/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py              # FastAPI app entry point
  │   ├── routers/
  │   │   ├── __init__.py
  │   │   ├── upload.py        # Document upload endpoint
  │   │   ├── process.py       # Bedrock processing endpoint
  │   │   └── results.py       # Results retrieval endpoint
  │   ├── services/
  │   │   ├── __init__.py
  │   │   ├── bedrock_service.py   # Bedrock API integration
  │   │   ├── s3_service.py        # S3 operations
  │   │   └── dynamodb_service.py  # DynamoDB operations
  │   ├── models/
  │   │   ├── __init__.py
  │   │   └── schemas.py       # Pydantic models
  │   └── config.py            # Configuration management
  ├── tests/
  │   └── test_bedrock.py
  ├── requirements.txt
  └── README.md
  ```
- [ ] Create `.env` file for local development:
  ```
  AWS_REGION=us-east-1
  AWS_ACCESS_KEY_ID=your_key
  AWS_SECRET_ACCESS_KEY=your_secret
  S3_BUCKET_NAME=medextract-documents
  DYNAMODB_TABLE_NAME=medextract-results
  ```
- [ ] Implement S3 service: upload, download, list files
- [ ] Implement DynamoDB service: put item, get item, query
- [ ] Create basic FastAPI endpoints (no Bedrock yet):
  - `POST /api/upload` - Upload document to S3
  - `GET /api/documents` - List uploaded documents
  - `GET /api/results/{document_id}` - Get extraction results
- [ ] Test locally with `uvicorn app.main:app --reload`

#### Deliverables:
- Working FastAPI backend with S3 and DynamoDB integration
- Local server running on `http://localhost:8000`
- Postman/curl tests for each endpoint

---

### **Phase 2: AWS Bedrock Integration (Days 5-6)**
**Status:** 🔴 Not Started

#### Tasks:
- [ ] Study AWS Bedrock documentation:
  - Boto3 Bedrock runtime client
  - Claude 3 Haiku model ID: `anthropic.claude-3-haiku-20240307-v1:0`
  - Input/output formats (JSON schema)
- [ ] Implement `bedrock_service.py`:
  ```python
  import boto3
  import json
  
  class BedrockService:
      def __init__(self):
          self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
          self.model_id = 'anthropic.claude-3-haiku-20240307-v1:0'
      
      def extract_medical_data(self, document_text: str) -> dict:
          # Prompt engineering for medical extraction
          prompt = self._build_extraction_prompt(document_text)
          response = self.client.invoke_model(
              modelId=self.model_id,
              body=json.dumps({
                  "anthropic_version": "bedrock-2023-05-31",
                  "max_tokens": 2000,
                  "messages": [{"role": "user", "content": prompt}]
              })
          )
          return json.loads(response['body'].read())
  ```
- [ ] Design medical data extraction prompt:
  - Extract: patient name, DOB, diagnoses, medications, lab values
  - Return structured JSON format
  - Handle missing/incomplete data gracefully
- [ ] Implement `POST /api/process/{document_id}` endpoint:
  - Retrieve document from S3
  - Extract text (handle PDFs with `PyPDF2` or `pdfplumber`)
  - Call Bedrock for extraction
  - Store results in DynamoDB
  - Return processing status + results
- [ ] Test with sample medical documents:
  - Create `sample-data/` folder with anonymized medical notes
  - Test extraction accuracy
  - Iterate on prompt engineering
- [ ] Add error handling:
  - Bedrock throttling (rate limits)
  - Invalid document formats
  - Extraction failures
- [ ] Add logging with Python `logging` module

#### Deliverables:
- Working Bedrock integration with medical text extraction
- Tested with 5+ sample documents
- Structured JSON output format defined

---

### **Phase 3: Frontend Development (Days 7-8)**
**Status:** 🔴 Not Started

#### Tasks:
- [ ] Create React app with TypeScript:
  ```bash
  npx create-react-app frontend --template typescript
  cd frontend
  npm install axios react-dropzone tailwindcss
  npx tailwindcss init
  ```
- [ ] Set up project structure:
  ```
  frontend/
  ├── src/
  │   ├── components/
  │   │   ├── FileUpload.tsx      # Drag-drop upload
  │   │   ├── DocumentList.tsx    # List uploaded docs
  │   │   ├── ResultsDisplay.tsx  # Show extracted data
  │   │   └── ProcessingStatus.tsx # Loading states
  │   ├── services/
  │   │   └── api.ts              # Axios API client
  │   ├── types/
  │   │   └── index.ts            # TypeScript interfaces
  │   ├── App.tsx
  │   └── index.tsx
  ├── public/
  ├── tailwind.config.js
  └── package.json
  ```
- [ ] Implement TypeScript interfaces:
  ```typescript
  interface Document {
    id: string;
    filename: string;
    uploadedAt: string;
    status: 'uploaded' | 'processing' | 'completed' | 'failed';
  }
  
  interface ExtractionResult {
    documentId: string;
    patientName?: string;
    dateOfBirth?: string;
    diagnoses: string[];
    medications: string[];
    labValues: Record<string, any>;
    extractedAt: string;
  }
  ```
- [ ] Build UI components:
  - **FileUpload:** Drag-drop zone with react-dropzone
  - **DocumentList:** Table of uploaded documents
  - **ResultsDisplay:** Formatted extraction results
  - **ProcessingStatus:** Progress indicator
- [ ] Implement API client (`services/api.ts`):
  ```typescript
  import axios from 'axios';
  
  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
  
  export const uploadDocument = (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return axios.post(`${API_BASE}/upload`, formData);
  };
  
  export const processDocument = (documentId: string) => {
    return axios.post(`${API_BASE}/process/${documentId}`);
  };
  
  export const getResults = (documentId: string) => {
    return axios.get(`${API_BASE}/results/${documentId}`);
  };
  ```
- [ ] Style with TailwindCSS - clean, professional medical theme
- [ ] Add CORS configuration in FastAPI backend
- [ ] Test full workflow: upload → process → view results

#### Deliverables:
- Working React frontend connected to backend
- Professional UI with responsive design
- End-to-end document processing workflow

---

### **Phase 4: AWS Deployment (Days 9-10)**
**Status:** 🔴 Not Started

#### Tasks:
- [ ] Create AWS infrastructure with CDK:
  ```bash
  mkdir infrastructure
  cd infrastructure
  npx cdk init app --language=typescript
  ```
- [ ] Define CDK stacks:
  - **S3 Stack:** Document storage bucket with versioning
  - **DynamoDB Stack:** Results table with TTL
  - **Lambda Stack:** Python function with layers
  - **API Gateway Stack:** REST API with CORS
  - **CloudWatch Stack:** Log groups and alarms
- [ ] Package Lambda function:
  - Create Lambda layer for dependencies (`boto3`, `fastapi-slim`)
  - Bundle FastAPI code into deployment package
  - Configure environment variables
- [ ] Deploy backend:
  ```bash
  cd infrastructure
  cdk deploy --all
  ```
- [ ] Configure API Gateway:
  - Enable CORS for frontend origin
  - Set up request validation
  - Add API key (optional)
- [ ] Deploy frontend to S3 + CloudFront (or Vercel for speed):
  ```bash
  cd frontend
  npm run build
  aws s3 sync build/ s3://medextract-frontend
  ```
- [ ] Test deployed application:
  - Upload document via deployed frontend
  - Verify S3 storage
  - Check DynamoDB results
  - Review CloudWatch logs

#### Deliverables:
- Fully deployed application on AWS
- CDK code in `infrastructure/` folder
- Deployment documentation in README

---

### **Phase 5: MLOps Enhancements (Days 11-12 - Optional)**
**Status:** 🔴 Not Started

#### Tasks:
- [ ] **Prompt Versioning:**
  - Store prompt templates in DynamoDB
  - Track which prompt version was used for each extraction
  - UI to select/compare prompt versions
- [ ] **A/B Testing:**
  - Compare Claude 3 Haiku vs Claude 3 Sonnet extraction quality
  - Store both results, flag differences
  - Calculate accuracy metrics
- [ ] **Monitoring Dashboard:**
  - CloudWatch dashboard with:
    - Request count by endpoint
    - Average processing time
    - Error rate
    - Bedrock API cost tracking
  - Export metrics to CSV for analysis
- [ ] **Model Performance Tracking:**
  - Store extraction confidence scores
  - Manual validation UI (mark extractions as correct/incorrect)
  - Calculate precision/recall over time
- [ ] **Automated Testing:**
  - Unit tests for all services (pytest)
  - E2E tests with Playwright
  - CI/CD pipeline with GitHub Actions:
    ```yaml
    name: Test & Deploy
    on: [push]
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v3
          - run: pip install -r requirements.txt
          - run: pytest
      deploy:
        needs: test
        runs-on: ubuntu-latest
        steps:
          - run: cdk deploy --all
    ```

#### Deliverables:
- Prompt versioning system
- A/B testing comparison feature
- CloudWatch monitoring dashboard
- Test suite with >70% coverage
- CI/CD pipeline

---

### **Phase 6: Documentation & Demo Prep (Day 13)**
**Status:** 🔴 Not Started

#### Tasks:
- [ ] Write comprehensive README:
  - Project overview with use case
  - Architecture diagram (use draw.io or Excalidraw)
  - Tech stack explanation
  - Setup instructions (local + AWS)
  - API documentation
  - Demo video link
- [ ] Create architecture diagrams:
  - High-level system architecture
  - Data flow diagram
  - AWS service connections
- [ ] Record demo video (5-7 minutes):
  - Show live upload of medical document
  - Explain Bedrock processing
  - Display structured extraction results
  - Highlight MLOps features (versioning, monitoring)
  - Discuss design decisions
- [ ] Prepare interview talking points:
  - Technical challenges faced
  - Design decisions (why DynamoDB vs RDS, why Claude 3 Haiku)
  - Cost optimization strategies
  - Production readiness improvements
- [ ] Add sample data:
  - 5-10 anonymized medical documents in `sample-data/`
  - Include variety: doctor notes, lab reports, prescriptions
- [ ] Clean up code:
  - Remove debug statements
  - Add docstrings to all functions
  - Format with `black` (Python) and `prettier` (TypeScript)
  - Update `.gitignore` to exclude sensitive files

#### Deliverables:
- Professional README with diagrams
- Demo video uploaded to YouTube/Loom
- Clean, documented codebase
- Interview preparation document

---

## 🎯 MVP vs Full Feature Set

### **MVP (Week 1 - Must Have):**
- ✅ React frontend with file upload
- ✅ Python FastAPI backend
- ✅ AWS Bedrock integration (Claude 3)
- ✅ S3 document storage
- ✅ DynamoDB results storage
- ✅ Basic extraction: patient info, diagnoses, medications
- ✅ Local development working
- ✅ Basic deployment to AWS

### **Full Feature Set (Week 2 - Nice to Have):**
- 🎁 Prompt versioning
- 🎁 A/B testing (compare models)
- 🎁 CloudWatch monitoring dashboard
- 🎁 Automated tests (unit + E2E)
- 🎁 CI/CD pipeline
- 🎁 CDK Infrastructure as Code
- 🎁 Manual validation UI

---

## 💰 Cost Tracking

| Service | Free Tier | Expected Cost (Development) |
|---------|-----------|----------------------------|
| AWS Bedrock (Claude 3 Haiku) | None | $0.00025/1K input tokens, $0.00125/1K output tokens (~$0.05/doc) |
| Lambda | 1M requests/month | $0 (within free tier) |
| API Gateway | 1M requests/month | $0 (within free tier) |
| S3 | 5GB storage, 20K GET, 2K PUT | $0 (within free tier) |
| DynamoDB | 25GB storage, 25 read/write units | $0 (within free tier) |
| CloudWatch | 5GB logs, 10 metrics | $0 (within free tier) |
| **Total Estimate** | | **<$10-20** for 100-200 test documents |

**Cost Optimization Tips:**
- Use Claude 3 Haiku (cheapest Bedrock model)
- Delete test documents from S3 after testing
- Set DynamoDB TTL to auto-delete old results
- Use S3 lifecycle policies

---

## 🚨 Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Bedrock access approval delayed | 🔴 High | Request immediately, have backup plan (OpenAI API) |
| Python inexperience slows development | 🟡 Medium | Use FastAPI docs, Cursor/Windsurf for code gen |
| CDK complexity | 🟡 Medium | Start with simple stacks, use CDK examples |
| Prompt engineering iterations | 🟢 Low | Allocate 1 day for prompt tuning |
| AWS costs exceed budget | 🟢 Low | Monitor billing daily, set budget alerts |
| Interview before completion | 🟡 Medium | Prioritize MVP, show WIP if needed |

---

## 🗣️ Interview Talking Points

**"What I Built:"**
> "I built MedExtract, a Gen AI application that extracts structured data from unstructured medical documents using AWS Bedrock. It mirrors your underwriting use case where you're structuring medical data to apply to decision rules. The app uses Claude 3 via Bedrock to extract patient information, diagnoses, medications, and lab values from doctor's notes and reports."

**"Technical Challenges:"**
> "The biggest challenge was prompt engineering for medical domain accuracy. Medical terminology is complex—diagnoses like 'Type 2 Diabetes Mellitus' vs 'T2DM' need normalization. I iterated on prompts to handle abbreviations, extract confidence scores, and gracefully handle incomplete data. I also implemented versioning so I could A/B test different prompt strategies."

**"Why These Technology Choices:"**
> "I chose Claude 3 Haiku for cost efficiency during development—it's 10x cheaper than Sonnet while maintaining good accuracy for extraction tasks. DynamoDB over RDS because the data model is simple key-value lookups and I wanted fast reads. FastAPI over Flask because it has built-in OpenAPI docs and async support for better Lambda performance."

**"Production Readiness:"**
> "For production, I'd add: comprehensive error handling with retries for Bedrock throttling, data validation schemas with Pydantic, end-to-end encryption for PHI, HIPAA compliance audit logging, automated testing with >80% coverage, and monitoring alerts for extraction accuracy degradation over time."

**"Learning Outcomes:"**
> "This project taught me AWS Bedrock integration patterns, prompt engineering for domain-specific tasks, serverless architecture on AWS, and MLOps basics like versioning and monitoring. I went from zero Bedrock experience to shipping a working application in 2 weeks—that's the same learning agility I'd bring to your team."

---

## 📋 Daily Standup Template

**Use this to track progress:**

### Today's Goals:
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

### Blockers:
- None / [describe blocker]

### Tomorrow's Plan:
- Task 1
- Task 2

### Notes:
- Any learnings, decisions, or questions

---

## ✅ Definition of Done

**Project is complete when:**
- [ ] Application deployed to AWS and publicly accessible
- [ ] Can upload medical document via UI
- [ ] Bedrock successfully extracts structured data
- [ ] Results displayed in formatted UI
- [ ] README with architecture diagram completed
- [ ] Demo video recorded and uploaded
- [ ] GitHub repo is public and polished
- [ ] Interview talking points prepared
- [ ] Total AWS costs < $20

---

## 🔗 Resources

### Documentation:
- [AWS Bedrock Developer Guide](https://docs.aws.amazon.com/bedrock/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Boto3 Bedrock Runtime](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html)
- [AWS CDK TypeScript Guide](https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-typescript.html)

### Sample Medical Documents (Anonymized):
- [MTSamples Medical Transcription](https://www.mtsamples.com/)
- [MIMIC-III Clinical Notes](https://physionet.org/content/mimiciii/) (requires training)

### YouTube Tutorials:
- "AWS Bedrock Tutorial for Beginners"
- "FastAPI Full Course"
- "React TypeScript Project Setup"

---

## 🚀 Next Steps

1. **Request Bedrock Access NOW** (don't wait)
2. **Set up AWS account** and configure CLI
3. **Create GitHub repo** and initialize project structure
4. **Start with Phase 1** (Backend Foundation)
5. **Update this plan daily** with progress and blockers

---

**Let's build this! 💪**

*Last Updated: 2025-12-04*
