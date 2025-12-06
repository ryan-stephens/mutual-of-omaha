"""
Experimentation and MLOps endpoints

Production endpoints for A/B testing, metrics analysis, and experiment management.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.services.metrics_service import MetricsService
from app.services.experiment_service import (
    ExperimentService,
    Experiment,
    ExperimentStatus,
    TrafficAllocation,
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

metrics_service = MetricsService()
experiment_service = ExperimentService()


# Request/Response Models


class PromptMetricsResponse(BaseModel):
    """Metrics for a single prompt version"""

    prompt_version: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float

    avg_processing_time_ms: float
    p50_processing_time_ms: float
    p95_processing_time_ms: float
    p99_processing_time_ms: float

    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    avg_cost_per_request: float

    avg_field_completeness: float
    avg_fields_extracted: float

    first_request: datetime
    last_request: datetime


class ComparisonRequest(BaseModel):
    """Request to compare two prompt versions"""

    control_version: str = Field(..., description="Baseline prompt version")
    treatment_version: str = Field(..., description="New prompt version to test")
    confidence_level: float = Field(
        0.95, ge=0.5, le=0.99, description="Statistical confidence level"
    )


class ComparisonResponse(BaseModel):
    """Statistical comparison between prompt versions"""

    control_version: str
    treatment_version: str

    control_n: int
    treatment_n: int

    control_success_rate: float
    treatment_success_rate: float
    success_rate_delta: float
    success_rate_p_value: float

    control_avg_time: float
    treatment_avg_time: float
    time_delta_ms: float
    time_p_value: float

    control_avg_cost: float
    treatment_avg_cost: float
    cost_delta_usd: float
    cost_delta_pct: float

    is_significant: bool
    confidence_level: float
    recommendation: str


class CreateExperimentRequest(BaseModel):
    """Request to create new experiment"""

    name: str = Field(..., description="Experiment name")
    description: str = Field(..., description="What is being tested")
    control_version: str = Field(..., description="Baseline prompt version")
    treatment_version: str = Field(..., description="New prompt version")
    traffic_allocation: TrafficAllocation = Field(TrafficAllocation.EQUAL_SPLIT)
    target_sample_size: int = Field(100, ge=30, description="Minimum samples per variant")
    max_duration_days: int = Field(30, ge=1, le=90)
    min_success_rate_delta: float = Field(5.0, ge=0, description="Minimum improvement (%)")
    max_cost_increase_pct: float = Field(20.0, ge=0, description="Maximum cost increase (%)")


class ExperimentResponse(BaseModel):
    """Experiment details"""

    experiment_id: str
    name: str
    description: str
    control_version: str
    treatment_version: str
    traffic_allocation: str
    target_sample_size: int
    max_duration_days: int
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    control_requests: int
    treatment_requests: int
    winner: Optional[str]
    conclusion: Optional[str]


# Endpoints


@router.get("/metrics/prompts/{prompt_version}", response_model=PromptMetricsResponse)
async def get_prompt_metrics(
    prompt_version: str,
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
):
    """
    Get comprehensive metrics for a prompt version

    Returns:
    - Success rate and error rate
    - Latency percentiles (p50, p95, p99)
    - Token usage and cost
    - Field completeness metrics
    """
    try:
        metrics = metrics_service.get_prompt_metrics(prompt_version)

        if not metrics:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for prompt version: {prompt_version}",
            )

        return PromptMetricsResponse(
            prompt_version=metrics.prompt_version,
            total_requests=metrics.total_requests,
            successful_requests=metrics.successful_requests,
            failed_requests=metrics.failed_requests,
            success_rate=metrics.success_rate,
            avg_processing_time_ms=metrics.avg_processing_time_ms,
            p50_processing_time_ms=metrics.p50_processing_time_ms,
            p95_processing_time_ms=metrics.p95_processing_time_ms,
            p99_processing_time_ms=metrics.p99_processing_time_ms,
            total_input_tokens=metrics.total_input_tokens,
            total_output_tokens=metrics.total_output_tokens,
            total_cost_usd=metrics.total_cost_usd,
            avg_cost_per_request=metrics.avg_cost_per_request,
            avg_field_completeness=metrics.avg_field_completeness,
            avg_fields_extracted=metrics.avg_fields_extracted,
            first_request=metrics.first_request,
            last_request=metrics.last_request,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metrics/compare", response_model=ComparisonResponse)
async def compare_prompt_versions(request: ComparisonRequest):
    """
    Statistically compare two prompt versions (A/B test analysis)

    Returns:
    - Success rate delta with p-value
    - Processing time comparison
    - Cost comparison
    - Statistical significance
    - Recommendation (promote/keep/continue testing)
    """
    try:
        result = metrics_service.compare_prompts(
            control_version=request.control_version,
            treatment_version=request.treatment_version,
            confidence_level=request.confidence_level,
        )

        if not result:
            raise HTTPException(status_code=400, detail="Insufficient data for comparison")

        return ComparisonResponse(
            control_version=result.control_version,
            treatment_version=result.treatment_version,
            control_n=result.control_n,
            treatment_n=result.treatment_n,
            control_success_rate=result.control_success_rate,
            treatment_success_rate=result.treatment_success_rate,
            success_rate_delta=result.success_rate_delta,
            success_rate_p_value=result.success_rate_p_value,
            control_avg_time=result.control_avg_time,
            treatment_avg_time=result.treatment_avg_time,
            time_delta_ms=result.time_delta_ms,
            time_p_value=result.time_p_value,
            control_avg_cost=result.control_avg_cost,
            treatment_avg_cost=result.treatment_avg_cost,
            cost_delta_usd=result.cost_delta_usd,
            cost_delta_pct=result.cost_delta_pct,
            is_significant=result.is_significant,
            confidence_level=result.confidence_level,
            recommendation=result.recommendation,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to compare prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experiments", response_model=ExperimentResponse)
async def create_experiment(request: CreateExperimentRequest):
    """
    Create a new A/B experiment

    Sets up experiment configuration for testing a new prompt version
    against the current production version.
    """
    try:
        experiment = experiment_service.create_experiment(
            name=request.name,
            description=request.description,
            control_version=request.control_version,
            treatment_version=request.treatment_version,
            traffic_allocation=request.traffic_allocation,
            target_sample_size=request.target_sample_size,
            max_duration_days=request.max_duration_days,
            min_success_rate_delta=request.min_success_rate_delta,
            max_cost_increase_pct=request.max_cost_increase_pct,
        )

        return _experiment_to_response(experiment)

    except Exception as e:
        logger.error(f"Failed to create experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/experiments", response_model=List[ExperimentResponse])
async def list_experiments(
    status: Optional[ExperimentStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
):
    """List all experiments, optionally filtered by status"""
    try:
        experiments = experiment_service.list_experiments(status=status, limit=limit)
        return [_experiment_to_response(exp) for exp in experiments]
    except Exception as e:
        logger.error(f"Failed to list experiments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(experiment_id: str):
    """Get experiment details by ID"""
    try:
        experiment = experiment_service.get_experiment(experiment_id)
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        return _experiment_to_response(experiment)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experiments/{experiment_id}/start")
async def start_experiment(experiment_id: str):
    """Start running an experiment"""
    try:
        success = experiment_service.start_experiment(experiment_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to start experiment")
        return {"message": "Experiment started", "experiment_id": experiment_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experiments/{experiment_id}/complete")
async def complete_experiment(
    experiment_id: str,
    winner: str = Query(..., description="Winning version"),
    conclusion: str = Query(..., description="Summary of results"),
):
    """Complete an experiment with results"""
    try:
        success = experiment_service.complete_experiment(
            experiment_id=experiment_id, winner=winner, conclusion=conclusion
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to complete experiment")
        return {
            "message": "Experiment completed",
            "experiment_id": experiment_id,
            "winner": winner,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experiments/{experiment_id}/promote")
async def promote_experiment(experiment_id: str):
    """Promote treatment version to production"""
    try:
        success = experiment_service.promote_treatment(experiment_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to promote treatment")
        return {
            "message": "Treatment promoted to production",
            "experiment_id": experiment_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to promote treatment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions


def _experiment_to_response(experiment: Experiment) -> ExperimentResponse:
    """Convert Experiment to response model"""
    return ExperimentResponse(
        experiment_id=experiment.experiment_id,
        name=experiment.name,
        description=experiment.description,
        control_version=experiment.control_version,
        treatment_version=experiment.treatment_version,
        traffic_allocation=experiment.traffic_allocation.value,
        target_sample_size=experiment.target_sample_size,
        max_duration_days=experiment.max_duration_days,
        status=experiment.status.value,
        created_at=experiment.created_at,
        started_at=experiment.started_at,
        ended_at=experiment.ended_at,
        control_requests=experiment.control_requests,
        treatment_requests=experiment.treatment_requests,
        winner=experiment.winner,
        conclusion=experiment.conclusion,
    )
