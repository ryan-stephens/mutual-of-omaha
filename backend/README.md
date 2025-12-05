# MedExtract Backend

FastAPI backend for medical document intelligence using AWS Bedrock.

## Setup

### 1. Create Virtual Environment

```powershell
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment

```powershell
# Copy example env file
copy .env.example .env

# Edit .env with your AWS credentials
# You can leave AWS credentials empty if using AWS CLI configured credentials
```

### 4. Run the Server

```powershell
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use Python directly
python -m app.main
```

Server will start at: http://localhost:8000

## API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

## API Endpoints

### Upload Document
```http
POST /api/upload
Content-Type: multipart/form-data

file: <medical_document.pdf>
```

### Process Document
```http
POST /api/process/{document_id}
Content-Type: application/json

{
    "document_id": "uuid",
    "prompt_version": "v1"
}
```

### Get Results
```http
GET /api/results/{document_id}
```

### List Documents
```http
GET /api/documents
```

### Delete Document
```http
DELETE /api/results/{document_id}
```

## Testing

Run the test suite:

```powershell
pytest tests/ -v
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── upload.py        # Upload endpoint
│   │   ├── process.py       # Processing endpoint
│   │   └── results.py       # Results endpoint
│   └── services/
│       ├── __init__.py
│       ├── s3_service.py        # S3 operations
│       ├── dynamodb_service.py  # DynamoDB operations
│       └── bedrock_service.py   # Bedrock AI integration
├── tests/
│   └── test_bedrock.py
├── requirements.txt
└── README.md
```

## AWS Services Used

- **S3:** Document storage
- **DynamoDB:** Metadata and results storage
- **Bedrock:** Claude 3 for medical data extraction
- **CloudWatch:** Logging (automatic)

## Environment Variables

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your_key>
AWS_SECRET_ACCESS_KEY=<your_secret>
S3_BUCKET_NAME=medextract-documents
DYNAMODB_TABLE_NAME=medextract-results
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
APP_ENV=development
LOG_LEVEL=INFO
```

## Development Tips

### Check Logs
Server logs show all AWS operations and errors.

### Test Bedrock Access
```powershell
python test_bedrock.py
```

### Format Code
```powershell
black app/
```

### Lint Code
```powershell
flake8 app/
```

## Troubleshooting

**Import errors?**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt`

**AWS credentials not working?**
- Check `.env` file or AWS CLI configuration
- Run `aws sts get-caller-identity` to verify

**Bedrock access denied?**
- Verify model access is approved in Bedrock console
- Check IAM permissions include `bedrock:InvokeModel`

**S3 bucket creation failed?**
- Bucket names must be globally unique
- Change `S3_BUCKET_NAME` in `.env`

## Next Steps

1. Start the backend server
2. Test with the Swagger UI at `/api/docs`
3. Upload a sample medical document
4. Process it and view extracted data
5. Build the React frontend to connect to this API
