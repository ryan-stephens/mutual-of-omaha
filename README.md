# MedExtract - Medical Document Intelligence

AI-powered medical document extraction system using AWS Bedrock, built to demonstrate Gen AI capabilities for healthcare applications.

## 🎯 Project Overview

**MedExtract** extracts structured data from unstructured medical documents (doctor's notes, lab reports, prescriptions) using AWS Bedrock's Claude 3 models. This project demonstrates:

- ✅ **AWS Bedrock Integration** - Claude 3 for medical text extraction
- ✅ **Full-Stack Development** - React TypeScript frontend + Python FastAPI backend
- ✅ **Cloud Infrastructure** - S3, DynamoDB, Lambda, API Gateway
- ✅ **MLOps Practices** - Prompt versioning, monitoring, A/B testing
- ✅ **Healthcare Domain** - Medical data extraction and structuring

## 🏗️ Architecture

```
React Frontend (TypeScript)
    ↓ HTTPS
AWS API Gateway
    ↓
Lambda (Python + FastAPI)
    ↓
├── S3 (Documents)
├── Bedrock (Claude 3)
└── DynamoDB (Results)
    ↓
CloudWatch (Monitoring)
```

## 🚀 Quick Start

### Prerequisites

- ✅ Python 3.11+
- ✅ Node.js 20+
- ✅ AWS Account with Bedrock access
- ✅ AWS CLI configured

### Backend Setup

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your AWS credentials

# Run server
uvicorn app.main:app --reload
```

Server starts at: http://localhost:8000

API Docs: http://localhost:8000/api/docs

### Test the Backend

```powershell
# Test AWS Bedrock connection
python test_bedrock.py

# Upload sample document via API
# Use Swagger UI at http://localhost:8000/api/docs
# or curl:
curl -X POST "http://localhost:8000/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample-data/sample_medical_note.txt"
```

### Frontend Setup (Coming Soon)

```powershell
cd frontend
npm install
npm run dev
```

## 📦 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + TypeScript | User interface |
| **Styling** | TailwindCSS | Modern responsive design |
| **Backend** | Python 3.11 + FastAPI | REST API server |
| **AI/ML** | AWS Bedrock (Claude 3 Haiku) | Medical data extraction |
| **Storage** | AWS S3 | Document storage |
| **Database** | DynamoDB | Metadata & results |
| **Compute** | AWS Lambda | Serverless processing |
| **API** | API Gateway | API layer |
| **IaC** | AWS CDK (TypeScript) | Infrastructure as Code |
| **CI/CD** | GitHub Actions | Automated deployment |
| **Monitoring** | CloudWatch | Logs and metrics |

## 📂 Project Structure

```
mutual-of-omaha/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI app
│   │   ├── config.py       # Configuration
│   │   ├── models/         # Pydantic schemas
│   │   ├── routers/        # API endpoints
│   │   └── services/       # AWS service integrations
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
├── frontend/               # React TypeScript frontend (coming)
├── infrastructure/         # AWS CDK (coming)
├── sample-data/           # Test medical documents
├── test_bedrock.py        # Bedrock connection test
├── PROJECT_PLAN.md        # Detailed development plan
└── README.md              # This file
```

## 🔑 API Endpoints

### Upload Document
```http
POST /api/upload
Content-Type: multipart/form-data
Body: file (PDF, TXT, DOC, DOCX)
```

### Process Document
```http
POST /api/process/{document_id}
Body: {"prompt_version": "v1"}
```

### Get Results
```http
GET /api/results/{document_id}
```

### List Documents
```http
GET /api/documents
```

## 📊 Extracted Data Structure

```json
{
  "document_id": "uuid",
  "filename": "medical_note.txt",
  "status": "completed",
  "medical_data": {
    "patient_name": "John Smith",
    "date_of_birth": "1975-03-15",
    "diagnoses": [
      "Type 2 Diabetes Mellitus",
      "Hypertension",
      "Dyslipidemia"
    ],
    "medications": [
      "Metformin 500mg twice daily",
      "Lisinopril 40mg once daily",
      "Atorvastatin 40mg daily"
    ],
    "lab_values": {
      "hemoglobin_a1c": "8.2%",
      "fasting_glucose": "185 mg/dL"
    },
    "vital_signs": {
      "blood_pressure": "145/92 mmHg",
      "heart_rate": "82 bpm"
    },
    "allergies": ["Penicillin", "Sulfa drugs"]
  },
  "processing_time_ms": 2500,
  "token_usage": {
    "input_tokens": 450,
    "output_tokens": 120
  }
}
```

## 💰 Cost Estimates

| Service | Cost (Development) |
|---------|-------------------|
| Bedrock (Claude 3 Haiku) | ~$0.05/document |
| Lambda | Free tier (1M requests) |
| S3 | Free tier (5GB) |
| DynamoDB | Free tier (25GB) |
| **Total** | **<$20 for 100-200 docs** |

## 🎯 Interview Talking Points

### What I Built
> "MedExtract is a Gen AI application that extracts structured data from unstructured medical documents using AWS Bedrock. It directly mirrors the underwriting use case at Mutual of Omaha where you're structuring medical data to apply to decision rules."

### Technical Challenges
> "The biggest challenge was prompt engineering for medical domain accuracy. I had to handle medical abbreviations, normalize terminology (T2DM → Type 2 Diabetes Mellitus), and ensure graceful handling of incomplete data. I implemented prompt versioning to A/B test different strategies."

### Technology Choices
> "I chose Claude 3 Haiku for cost efficiency during development—it's 10x cheaper than Sonnet while maintaining good accuracy for extraction tasks. DynamoDB over RDS because the data model is simple key-value lookups. FastAPI over Flask for built-in async support and OpenAPI docs."

### Learning Outcomes
> "This project taught me AWS Bedrock integration patterns, prompt engineering for domain-specific tasks, serverless architecture on AWS, and MLOps basics like versioning and monitoring. I went from zero Bedrock experience to shipping a working application in under 2 weeks."

## 📚 Development Timeline

- ✅ **Day 0-2:** AWS setup, Bedrock access
- ✅ **Day 3-4:** Backend foundation (FastAPI, S3, DynamoDB)
- ✅ **Day 5-6:** Bedrock integration, prompt engineering
- 🔄 **Day 7-8:** React frontend (in progress)
- ⏳ **Day 9-10:** AWS deployment with CDK
- ⏳ **Day 11-12:** MLOps features (versioning, monitoring)
- ⏳ **Day 13:** Documentation and demo video

## 🔗 Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Project Plan](PROJECT_PLAN.md) - Detailed development roadmap

## 👤 Author

**Ryan Stephens**  
Senior Full-Stack Software Engineer  
ryan.stephens15@gmail.com  
[Portfolio](https://ryan-stephens.dev/)

Built for Mutual of Omaha Senior AI Developer position interview preparation.

---

**Current Status:** Backend MVP Complete ✅ | Frontend In Progress 🔄 | Deployment Pending ⏳
