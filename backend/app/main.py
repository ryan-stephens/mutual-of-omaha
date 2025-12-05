"""
Main FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, process, results, prompts, experiments
from app.config import settings
import logging

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="MedExtract API",
    description="Medical document intelligence using AWS Bedrock",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(process.router, prefix="/api", tags=["process"])
app.include_router(results.router, prefix="/api", tags=["results"])
app.include_router(prompts.router, prefix="/api", tags=["prompts"])
app.include_router(experiments.router, prefix="/api", tags=["experiments", "mlops"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"service": "MedExtract API", "status": "healthy", "version": "0.1.0"}


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "region": settings.AWS_REGION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
