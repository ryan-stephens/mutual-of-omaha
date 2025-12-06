# AWS Resource Viewer for MedExtract Platform
# Quick commands to view your deployed resources

Write-Host "🚀 MedExtract AWS Resources" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Lambda Functions
Write-Host "📦 Lambda Functions:" -ForegroundColor Cyan
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `"medextract`")].{Name:FunctionName, Runtime:Runtime, Memory:MemorySize, Timeout:Timeout}' --output table

Write-Host ""
Write-Host "🌐 API Gateway:" -ForegroundColor Cyan
aws apigateway get-rest-apis --query 'items[?contains(name, `"MedExtract`")].{Name:name, ID:id, Endpoint:id}' --output table

Write-Host ""
Write-Host "📊 DynamoDB Tables:" -ForegroundColor Cyan
aws dynamodb list-tables --query 'TableNames[?starts_with(@, `"medextract`")]' --output table

Write-Host ""
Write-Host "🪣 S3 Buckets:" -ForegroundColor Cyan
aws s3 ls | Select-String "medextract"

Write-Host ""
Write-Host "📝 Recent Lambda Logs (Upload):" -ForegroundColor Cyan
Write-Host "Last 5 log entries:" -ForegroundColor Yellow
aws logs tail /aws/lambda/medextract-upload-dev --since 10m --format short | Select-Object -Last 5

Write-Host ""
Write-Host "📝 Recent Lambda Logs (Extract):" -ForegroundColor Cyan
Write-Host "Last 5 log entries:" -ForegroundColor Yellow
aws logs tail /aws/lambda/medextract-extract-dev --since 10m --format short | Select-Object -Last 5

Write-Host ""
Write-Host "💰 Estimated Costs (Last 24h):" -ForegroundColor Cyan
Write-Host "Note: Costs may take 24h to appear" -ForegroundColor Yellow

Write-Host ""
Write-Host "🔗 Quick Links:" -ForegroundColor Green
Write-Host "Lambda Console:    https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions" -ForegroundColor White
Write-Host "API Gateway:       https://console.aws.amazon.com/apigateway/home?region=us-east-1#/apis" -ForegroundColor White
Write-Host "DynamoDB:          https://console.aws.amazon.com/dynamodbv2/home?region=us-east-1#tables" -ForegroundColor White
Write-Host "S3:                https://console.aws.amazon.com/s3/home?region=us-east-1" -ForegroundColor White
Write-Host "CloudWatch Logs:   https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups" -ForegroundColor White
Write-Host ""
Write-Host "Your API Gateway URL:" -ForegroundColor Yellow
Write-Host "https://kya7rp5m26.execute-api.us-east-1.amazonaws.com/dev/" -ForegroundColor Cyan
