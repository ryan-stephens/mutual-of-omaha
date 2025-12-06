"""
Lambda handler for metrics operations
"""

import logging
import sys
import os

sys.path.insert(0, "/opt/python")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import create_response, create_error_response, get_query_parameter
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

metrics_service = MetricsService()


def handler(event, context):
    """
    Process metrics requests

    Supports both:
    - GET /api/metrics/prompts/{version} - Get metrics for specific version
    - GET /api/metrics - Get all metrics (query param: prompt_version, days)
    - POST /api/metrics/compare - Compare two versions
    """
    # Handle CORS preflight requests
    if event.get("httpMethod") == "OPTIONS":
        return create_response(200, {"message": "OK"})

    try:
        logger.info(f"Metrics request received: {event.get('httpMethod')} {event.get('path')}")

        # Handle POST /api/metrics/compare
        if event.get("httpMethod") == "POST" and "compare" in event.get("path", ""):
            logger.info("Handling comparison request")
            body = event.get("body", "{}")
            import json

            data = json.loads(body) if isinstance(body, str) else body

            control_version = data.get("control_version")
            treatment_version = data.get("treatment_version")
            confidence_level = data.get("confidence_level", 0.95)

            if not control_version or not treatment_version:
                return create_error_response(400, "Missing control_version or treatment_version")

            if control_version == treatment_version:
                return create_error_response(
                    400, "Control and treatment versions must be different"
                )

            logger.info(
                f"Comparing {control_version} vs {treatment_version} at {confidence_level*100}% confidence"
            )

            try:
                result = metrics_service.compare_prompts(
                    control_version=control_version,
                    treatment_version=treatment_version,
                    confidence_level=confidence_level,
                )

                if not result:
                    return create_error_response(400, "Insufficient data for comparison")

                return create_response(
                    200,
                    {
                        "control_version": result.control_version,
                        "treatment_version": result.treatment_version,
                        "control_n": result.control_n,
                        "treatment_n": result.treatment_n,
                        "control_success_rate": result.control_success_rate,
                        "treatment_success_rate": result.treatment_success_rate,
                        "success_rate_delta": result.success_rate_delta,
                        "success_rate_p_value": result.success_rate_p_value,
                        "control_avg_time": result.control_avg_time,
                        "treatment_avg_time": result.treatment_avg_time,
                        "time_delta_ms": result.time_delta_ms,
                        "time_p_value": result.time_p_value,
                        "control_avg_cost": result.control_avg_cost,
                        "treatment_avg_cost": result.treatment_avg_cost,
                        "cost_delta_usd": result.cost_delta_usd,
                        "cost_delta_pct": result.cost_delta_pct,
                        "is_significant": result.is_significant,
                        "confidence_level": result.confidence_level,
                        "recommendation": result.recommendation,
                    },
                )
            except Exception as e:
                logger.error(f"Comparison failed: {str(e)}", exc_info=True)
                return create_error_response(500, f"Comparison failed: {str(e)}")

        # Handle GET /api/lambda/metrics - CloudWatch Lambda metrics
        if event.get("httpMethod") == "GET" and "/lambda/metrics" in event.get("path", ""):
            logger.info("Handling Lambda metrics request")
            from app.services.cloudwatch_service import CloudWatchService

            hours_str = get_query_parameter(event, "hours", "24")
            try:
                hours = int(hours_str)
            except ValueError:
                return create_error_response(400, "Invalid 'hours' parameter, must be integer")

            try:
                cloudwatch_service = CloudWatchService()
                metrics = cloudwatch_service.get_lambda_metrics(hours=hours)

                metrics_list = [
                    {
                        "function_name": m.function_name,
                        "invocations": m.invocations,
                        "errors": m.errors,
                        "throttles": m.throttles,
                        "avg_duration_ms": m.avg_duration_ms,
                        "p99_duration_ms": m.p99_duration_ms,
                        "cold_starts": m.cold_starts,
                        "memory_used_mb": m.memory_used_mb,
                        "memory_allocated_mb": m.memory_allocated_mb,
                        "cost_usd": m.cost_usd,
                    }
                    for m in metrics
                ]

                return create_response(200, metrics_list)
            except Exception as e:
                logger.error(f"Failed to get Lambda metrics: {str(e)}", exc_info=True)
                return create_error_response(500, f"Failed to get Lambda metrics: {str(e)}")

        # Extract version from path parameter if present
        path_params = event.get("pathParameters") or {}
        prompt_version = path_params.get("version") or get_query_parameter(event, "prompt_version")
        days_str = get_query_parameter(event, "days", "7")

        try:
            days = int(days_str)
        except ValueError:
            return create_error_response(400, "Invalid 'days' parameter, must be integer")

        if prompt_version:
            logger.info(f"Getting metrics for prompt version: {prompt_version}")

            # Calculate start_date from days parameter
            from datetime import datetime, timedelta

            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            logger.info(f"Querying metrics from {start_date} to {end_date}")

            try:
                metrics = metrics_service.get_prompt_metrics(
                    prompt_version, start_date=start_date, end_date=end_date
                )
            except Exception as e:
                logger.error(f"Exception in get_prompt_metrics: {str(e)}", exc_info=True)
                return create_error_response(500, f"Failed to retrieve metrics: {str(e)}")

            if not metrics:
                logger.warning(
                    f"No metrics returned for {prompt_version} in date range {start_date} to {end_date}"
                )
                return create_error_response(
                    404, f"No metrics found for prompt version: {prompt_version}"
                )

            return create_response(
                200,
                {
                    "prompt_version": metrics.prompt_version,
                    "total_requests": metrics.total_requests,
                    "successful_requests": metrics.successful_requests,
                    "failed_requests": metrics.failed_requests,
                    "success_rate": metrics.success_rate,
                    "avg_processing_time_ms": metrics.avg_processing_time_ms,
                    "p50_processing_time_ms": metrics.p50_processing_time_ms,
                    "p95_processing_time_ms": metrics.p95_processing_time_ms,
                    "p99_processing_time_ms": metrics.p99_processing_time_ms,
                    "total_input_tokens": metrics.total_input_tokens,
                    "total_output_tokens": metrics.total_output_tokens,
                    "total_cost_usd": metrics.total_cost_usd,
                    "avg_cost_per_request": metrics.avg_cost_per_request,
                    "avg_field_completeness": metrics.avg_field_completeness,
                    "avg_fields_extracted": metrics.avg_fields_extracted,
                    "first_request": (
                        metrics.first_request.isoformat() if metrics.first_request else None
                    ),
                    "last_request": (
                        metrics.last_request.isoformat() if metrics.last_request else None
                    ),
                },
            )
        else:
            logger.info(f"Getting all prompt metrics for last {days} days")
            all_metrics = metrics_service.get_all_prompt_metrics(days=days)

            metrics_list = []
            for m in all_metrics:
                metrics_list.append(
                    {
                        "prompt_version": m.prompt_version,
                        "total_requests": m.total_requests,
                        "success_rate": m.success_rate,
                        "avg_processing_time_ms": m.avg_processing_time_ms,
                        "total_cost_usd": m.total_cost_usd,
                        "avg_field_completeness": m.avg_field_completeness,
                    }
                )

            return create_response(
                200, {"metrics": metrics_list, "count": len(metrics_list), "days": days}
            )

    except Exception as e:
        logger.error(f"Metrics handler error: {e}", exc_info=True)
        return create_error_response(500, f"Failed to retrieve metrics: {str(e)}")
