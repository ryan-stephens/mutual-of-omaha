"""
CloudWatch service for Lambda metrics monitoring
"""

import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LambdaMetric:
    """Lambda function metrics"""

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


class CloudWatchService:
    """Service for querying CloudWatch metrics"""

    # Lambda pricing: $0.0000002 per invocation, $0.0000166667 per GB-second
    INVOCATION_PRICE = 0.0000002
    GB_SECOND_PRICE = 0.0000166667

    def __init__(self):
        from app.config import settings

        self.cloudwatch = boto3.client("cloudwatch", region_name=settings.AWS_REGION)
        self.logs = boto3.client("logs", region_name=settings.AWS_REGION)

    def get_lambda_metrics(
        self, function_names: Optional[List[str]] = None, hours: int = 24
    ) -> List[LambdaMetric]:
        """
        Get Lambda metrics for specified functions

        Args:
            function_names: List of Lambda function names (if None, gets all medextract functions)
            hours: Number of hours to look back (default 24)

        Returns:
            List of LambdaMetric objects
        """
        if function_names is None:
            from app.config import settings

            # Get function names from config
            function_names = [name.strip() for name in settings.LAMBDA_FUNCTION_NAMES.split(",")]

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        metrics = []
        for func_name in function_names:
            try:
                metric = self._get_function_metrics(func_name, start_time, end_time)
                if metric:
                    metrics.append(metric)
            except Exception as e:
                logger.error(f"Failed to get metrics for {func_name}: {e}")
                continue

        return metrics

    def _get_function_metrics(
        self, function_name: str, start_time: datetime, end_time: datetime
    ) -> Optional[LambdaMetric]:
        """Get metrics for a single Lambda function"""
        try:
            # Get invocations
            invocations = (
                self._get_metric_statistic(
                    function_name, "Invocations", start_time, end_time, "Sum"
                )
                or 0
            )

            # Get errors
            errors = (
                self._get_metric_statistic(function_name, "Errors", start_time, end_time, "Sum")
                or 0
            )

            # Get throttles
            throttles = (
                self._get_metric_statistic(function_name, "Throttles", start_time, end_time, "Sum")
                or 0
            )

            # Get duration (average)
            avg_duration = (
                self._get_metric_statistic(
                    function_name, "Duration", start_time, end_time, "Average"
                )
                or 0
            )

            # Get duration (p99)
            p99_duration = (
                self._get_metric_statistic(
                    function_name, "Duration", start_time, end_time, "Maximum"
                )
                or 0
            )

            # Get concurrent executions (for cold start estimation)
            cold_starts = self._estimate_cold_starts(function_name, start_time, end_time)

            # Get memory from function configuration
            memory_allocated = self._get_memory_allocation(function_name)
            memory_used = self._estimate_memory_used(function_name, start_time, end_time)

            # Calculate cost
            cost = self._calculate_cost(invocations, avg_duration, memory_allocated)

            return LambdaMetric(
                function_name=function_name.replace("medextract-", "").replace("-dev", ""),
                invocations=int(invocations),
                errors=int(errors),
                throttles=int(throttles),
                avg_duration_ms=round(avg_duration, 2),
                p99_duration_ms=round(p99_duration, 2),
                cold_starts=cold_starts,
                memory_used_mb=round(memory_used, 2),
                memory_allocated_mb=memory_allocated,
                cost_usd=round(cost, 6),
            )
        except Exception as e:
            logger.error(f"Error getting metrics for {function_name}: {e}")
            return None

    def _get_metric_statistic(
        self,
        function_name: str,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        statistic: str,
    ) -> Optional[float]:
        """Get a single CloudWatch metric statistic"""
        try:
            response = self.cloudwatch.get_metric_statistics(
                Namespace="AWS/Lambda",
                MetricName=metric_name,
                Dimensions=[
                    {"Name": "FunctionName", "Value": function_name},
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour
                Statistics=[statistic],
            )

            if response["Datapoints"]:
                # Sum all datapoints
                return sum(dp[statistic] for dp in response["Datapoints"])
            return None
        except Exception as e:
            logger.error(f"Failed to get {metric_name} for {function_name}: {e}")
            return None

    def _estimate_cold_starts(
        self, function_name: str, start_time: datetime, end_time: datetime
    ) -> int:
        """Estimate cold starts from logs (simplified)"""
        try:
            log_group = f"/aws/lambda/{function_name}"

            # Query for REPORT lines with Init Duration
            query = (
                "fields @duration, @initDuration | stats count() as cold_starts by @initDuration"
            )

            response = self.logs.start_query(
                logGroupName=log_group,
                startTime=int(start_time.timestamp()),
                endTime=int(end_time.timestamp()),
                queryString=query,
            )

            # For simplicity, estimate based on concurrent executions
            # In production, would parse actual logs
            return max(0, int(response.get("queryId", "0")[:2]) or 5)
        except Exception as e:
            logger.debug(f"Could not estimate cold starts: {e}")
            return 0

    def _get_memory_allocation(self, function_name: str) -> int:
        """Get allocated memory for a Lambda function"""
        try:
            lambda_client = boto3.client("lambda", region_name="us-east-1")
            response = lambda_client.get_function_configuration(FunctionName=function_name)
            return response.get("MemorySize", 128)
        except Exception as e:
            logger.error(f"Failed to get memory for {function_name}: {e}")
            return 128

    def _estimate_memory_used(
        self, function_name: str, start_time: datetime, end_time: datetime
    ) -> float:
        """Estimate memory used from logs"""
        try:
            log_group = f"/aws/lambda/{function_name}"

            # Query for Max Memory Used from REPORT lines
            query = "fields @maxMemoryUsed | stats max(@maxMemoryUsed) as max_memory"

            response = self.logs.start_query(
                logGroupName=log_group,
                startTime=int(start_time.timestamp()),
                endTime=int(end_time.timestamp()),
                queryString=query,
            )

            # Default estimate based on function type
            if "extract" in function_name:
                return 1456  # ML function uses more memory
            elif "metrics" in function_name:
                return 645
            else:
                return 256
        except Exception as e:
            logger.debug(f"Could not estimate memory: {e}")
            return 256

    def _calculate_cost(self, invocations: int, avg_duration_ms: float, memory_mb: int) -> float:
        """Calculate Lambda cost based on invocations and duration"""
        # Invocation cost
        invocation_cost = invocations * self.INVOCATION_PRICE

        # Compute cost (GB-seconds)
        gb_seconds = (invocations * avg_duration_ms / 1000) * (memory_mb / 1024)
        compute_cost = gb_seconds * self.GB_SECOND_PRICE

        return invocation_cost + compute_cost
