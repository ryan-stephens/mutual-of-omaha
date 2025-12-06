"""
Lambda metrics endpoints for monitoring serverless performance
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from app.services.cloudwatch_service import CloudWatchService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

cloudwatch_service = CloudWatchService()


class LambdaMetricResponse(BaseModel):
    """Lambda function metric response"""
    function_name: str
    invocations: int
    errors: int
    throttles: int
    avg_duration_ms: float
    p99_duration_ms: float
    cold_starts: int
    memory_used_mb: float
    memory_allocated_mb: int
    cost_usd: float


@router.get("/lambda/metrics", response_model=List[LambdaMetricResponse])
async def get_lambda_metrics(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze"),
):
    """
    Get Lambda function metrics from CloudWatch

    Returns metrics for all medextract Lambda functions including:
    - Invocations and error rates
    - Duration (average and p99)
    - Cold starts
    - Memory utilization
    - Estimated cost
    """
    try:
        metrics = cloudwatch_service.get_lambda_metrics(hours=hours)

        return [
            LambdaMetricResponse(
                function_name=m.function_name,
                invocations=m.invocations,
                errors=m.errors,
                throttles=m.throttles,
                avg_duration_ms=m.avg_duration_ms,
                p99_duration_ms=m.p99_duration_ms,
                cold_starts=m.cold_starts,
                memory_used_mb=m.memory_used_mb,
                memory_allocated_mb=m.memory_allocated_mb,
                cost_usd=m.cost_usd,
            )
            for m in metrics
        ]

    except Exception as e:
        logger.error(f"Failed to get Lambda metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
