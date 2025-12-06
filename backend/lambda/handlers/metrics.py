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
    try:
        logger.info(
            f"Metrics request received: {event.get('httpMethod')} {event.get('path')}"
        )

        # Handle POST /api/metrics/compare
        if event.get("httpMethod") == "POST" and "compare" in event.get("path", ""):
            logger.info("Handling comparison request")
            body = event.get("body", "{}")
            import json

            data = json.loads(body) if isinstance(body, str) else body

            control_version = data.get("control_version")
            treatment_version = data.get("treatment_version")

            if not control_version or not treatment_version:
                return create_error_response(
                    400, "Missing control_version or treatment_version"
                )

            # For now, return a message that this endpoint needs implementation
            return create_response(
                200,
                {
                    "message": "Comparison endpoint not yet implemented",
                    "control_version": control_version,
                    "treatment_version": treatment_version,
                },
            )

        # Extract version from path parameter if present
        path_params = event.get("pathParameters") or {}
        prompt_version = path_params.get("version") or get_query_parameter(
            event, "prompt_version"
        )
        days_str = get_query_parameter(event, "days", "7")

        try:
            days = int(days_str)
        except ValueError:
            return create_error_response(
                400, "Invalid 'days' parameter, must be integer"
            )

        if prompt_version:
            logger.info(f"Getting metrics for prompt version: {prompt_version}")
            metrics = metrics_service.get_prompt_metrics(prompt_version, days=days)

            if not metrics:
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
                        metrics.first_request.isoformat()
                        if metrics.first_request
                        else None
                    ),
                    "last_request": (
                        metrics.last_request.isoformat()
                        if metrics.last_request
                        else None
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
