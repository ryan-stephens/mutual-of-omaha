# 🎉 AWS Lambda Deployment Complete!

**Deployment Date:** December 5, 2025  
**Environment:** dev  
**Status:** ✅ Successfully Deployed

---

## 📊 Deployment Summary

### API Gateway
- **URL:** `https://kya7rp5m26.execute-api.us-east-1.amazonaws.com/dev/`
- **Stage:** dev
- **CORS:** Enabled for localhost:3000, localhost:5173, localhost:5174

### Lambda Functions
| Function | ARN | Memory | Timeout |
|----------|-----|--------|---------|
| **Upload** | `arn:aws:lambda:us-east-1:688567279260:function:medextract-upload-dev` | 512 MB | 60s |
| **Extract** | `arn:aws:lambda:us-east-1:688567279260:function:medextract-extract-dev` | 1024 MB | 300s |
| **Metrics** | `arn:aws:lambda:us-east-1:688567279260:function:medextract-metrics-dev` | 1024 MB | 60s |
| **Experiment** | `arn:aws:lambda:us-east-1:688567279260:function:medextract-experiment-dev` | 512 MB | 60s |

### AWS Resources
- **S3 Bucket:** `medextract-documents-dev-688567279260`
- **DynamoDB Results Table:** `medextract-results-dev`
- **DynamoDB Experiments Table:** `medextract-experiments-dev`
- **IAM Role:** `MedExtractStack-dev-LambdaExecutionRoleD5C26073-C9SFW1L3DrYp`

---

## 🧪 Testing from Local Frontend

### Step 1: Frontend is Already Configured
The file `.env.development.local` has been created with:
```
VITE_API_BASE_URL=https://kya7rp5m26.execute-api.us-east-1.amazonaws.com/dev
```

### Step 2: Start Frontend
```powershell
cd frontend
npm run dev
```

### Step 3: Test the Flow
1. **Open:** `http://localhost:5174`
2. **Select prompt version** (dropdown will load from Lambda)
3. **Upload a document** → Calls Lambda upload function
4. **View extraction** → Calls Lambda extract function (Bedrock)
5. **Check console** → See logs with Lambda responses

### Expected Behavior
- ✅ Prompt versions load dynamically from `/api/prompts/versions`
- ✅ File upload goes to S3 via Lambda
- ✅ Extraction uses Bedrock via Lambda
- ✅ Results stored in DynamoDB
- ✅ Same experience as local FastAPI, but serverless!

---

## 🔍 API Endpoints

All endpoints are prefixed with `/api`:

### Upload
```
POST https://kya7rp5m26.execute-api.us-east-1.amazonaws.com/dev/api/upload
```

### Extract
```
POST https://kya7rp5m26.execute-api.us-east-1.amazonaws.com/dev/api/extract/{document_id}
Body: { "prompt_version": "v2.0.0" }
```

### Metrics
```
GET https://kya7rp5m26.execute-api.us-east-1.amazonaws.com/dev/api/metrics
GET https://kya7rp5m26.execute-api.us-east-1.amazonaws.com/dev/api/metrics/prompts/{version}
```

### Experiments
```
GET https://kya7rp5m26.execute-api.us-east-1.amazonaws.com/dev/api/experiments
POST https://kya7rp5m26.execute-api.us-east-1.amazonaws.com/dev/api/experiments
```

---

## 📊 Monitoring

### CloudWatch Logs
```powershell
# View Lambda logs
aws logs tail /aws/lambda/medextract-upload-dev --follow
aws logs tail /aws/lambda/medextract-extract-dev --follow
aws logs tail /aws/lambda/medextract-metrics-dev --follow
aws logs tail /aws/lambda/medextract-experiment-dev --follow
```

### X-Ray Tracing
- Navigate to AWS Console → X-Ray → Service Map
- View end-to-end request traces

### API Gateway Metrics
- Navigate to AWS Console → API Gateway → `medextract-api-dev`
- View request count, latency, errors

---

## 🐛 Troubleshooting

### If Frontend Can't Connect
1. Check browser console for CORS errors
2. Verify API Gateway URL in `.env.development.local`
3. Test API directly:
   ```powershell
   curl https://kya7rp5m26.execute-api.us-east-1.amazonaws.com/dev/api/health
   ```

### If Lambda Fails
1. Check CloudWatch Logs (see commands above)
2. Verify IAM permissions
3. Check Lambda environment variables in AWS Console

### If Bedrock Fails
1. Ensure Bedrock model access is enabled in AWS Console
2. Check Lambda has `bedrock:InvokeModel` permission
3. Verify prompt files exist in Lambda deployment package

---

## 💰 Cost Estimate

**Development usage (light testing):**
- Lambda: $0-2/month (within free tier)
- API Gateway: $0-1/month (within free tier)
- DynamoDB: $0 (within free tier)
- S3: $0-0.50/month
- Bedrock: $0.05-0.50/month (depends on usage)
- **Total: ~$1-4/month**

---

## 🔄 Update Deployment

To deploy code changes:
```powershell
cd infrastructure
cdk deploy -c env=dev --all
```

CDK automatically:
- Packages Lambda code
- Uploads to S3
- Updates Lambda functions
- Zero downtime deployment

---

## 🎯 Next Steps

1. ✅ **Test from local frontend** - Verify everything works
2. ⏳ **Deploy frontend to production** - Vercel or S3+CloudFront
3. ⏳ **Set up monitoring alerts** - CloudWatch alarms
4. ⏳ **Add API authentication** - API Gateway API keys
5. ⏳ **Enable API Gateway logging** - Set up CloudWatch Logs role

---

## 📚 Documentation

- **Deployment Guide:** `docs/DEPLOYMENT.md`
- **Architecture:** `HYBRID_ARCHITECTURE.md`
- **Lambda Architecture:** `docs/LAMBDA_ARCHITECTURE.md`

---

**Deployment successful! Your backend is now running serverless on AWS Lambda!** 🚀
