# Install Lambda dependencies locally
Write-Host "Installing Lambda dependencies..." -ForegroundColor Green

# Create lambda_package directory
$packageDir = "lambda_package"
if (Test-Path $packageDir) {
    Remove-Item -Recurse -Force $packageDir
}
New-Item -ItemType Directory -Path $packageDir | Out-Null

# Install only required dependencies (not dev dependencies)
pip install `
    pydantic==2.10.5 `
    pydantic-settings==2.7.1 `
    PyPDF2==3.0.1 `
    pdfplumber==0.10.3 `
    python-dotenv==1.0.0 `
    -t $packageDir

# Copy app code
Copy-Item -Recurse -Path "app" -Destination "$packageDir/app"
Copy-Item -Recurse -Path "lambda" -Destination "$packageDir/lambda"
Copy-Item -Recurse -Path "prompts" -Destination "$packageDir/prompts"

Write-Host "Dependencies installed to $packageDir" -ForegroundColor Green
Write-Host "Update CDK to use: lambda_.Code.from_asset('../backend/lambda_package')" -ForegroundColor Yellow
