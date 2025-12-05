"""
Experiment Management Service

Production-grade A/B testing and experimentation framework for prompt optimization.
Manages experiment lifecycle: setup → run → analyze → promote/rollback.
"""

import boto3
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class ExperimentStatus(str, Enum):
    """Experiment lifecycle states"""

    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    PROMOTED = "promoted"
    ROLLED_BACK = "rolled_back"


class TrafficAllocation(str, Enum):
    """Traffic split strategies"""

    EQUAL_SPLIT = "50/50"
    CONTROL_HEAVY = "80/20"
    TREATMENT_HEAVY = "20/80"
    CANARY = "95/5"


@dataclass
class Experiment:
    """Experiment definition"""

    experiment_id: str
    name: str
    description: str

    # Versions under test
    control_version: str
    treatment_version: str

    # Configuration
    traffic_allocation: TrafficAllocation
    target_sample_size: int
    max_duration_days: int

    # Success criteria
    min_success_rate_delta: float  # Minimum improvement to promote
    max_cost_increase_pct: float  # Maximum acceptable cost increase

    # Metadata
    status: ExperimentStatus
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_by: str

    # Results
    control_requests: int = 0
    treatment_requests: int = 0
    winner: Optional[str] = None
    conclusion: Optional[str] = None


class ExperimentService:
    """
    Manages A/B experiments for prompt optimization.

    Features:
    - Experiment lifecycle management
    - Traffic allocation and routing
    - Statistical analysis integration
    - Automated promotion/rollback
    - Experiment history and audit trail
    """

    def __init__(self, table_name: str = "medextract-experiments"):
        self.dynamodb = boto3.resource("dynamodb")
        self.table_name = table_name
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Create experiments table if it doesn't exist"""
        try:
            self.table = self.dynamodb.Table(self.table_name)
            self.table.load()
            logger.info(f"Experiments table exists: {self.table_name}")
        except Exception:
            logger.info(f"Creating experiments table: {self.table_name}")
            self.table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[{"AttributeName": "experiment_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "experiment_id", "AttributeType": "S"},
                    {"AttributeName": "created_at", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "CreatedAtIndex",
                        "KeySchema": [
                            {"AttributeName": "created_at", "KeyType": "HASH"}
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    }
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            self.table.wait_until_exists()
            logger.info("Experiments table created successfully")

    def create_experiment(
        self,
        name: str,
        description: str,
        control_version: str,
        treatment_version: str,
        traffic_allocation: TrafficAllocation = TrafficAllocation.EQUAL_SPLIT,
        target_sample_size: int = 100,
        max_duration_days: int = 30,
        min_success_rate_delta: float = 5.0,
        max_cost_increase_pct: float = 20.0,
        created_by: str = "system",
    ) -> Experiment:
        """
        Create a new experiment

        Args:
            name: Experiment name
            description: What is being tested
            control_version: Baseline prompt version
            treatment_version: New prompt version to test
            traffic_allocation: How to split traffic
            target_sample_size: Minimum samples needed per variant
            max_duration_days: Maximum experiment duration
            min_success_rate_delta: Minimum improvement to promote (%)
            max_cost_increase_pct: Maximum acceptable cost increase (%)
            created_by: User/system creating the experiment

        Returns:
            Created Experiment object
        """
        experiment_id = f"exp_{int(datetime.utcnow().timestamp())}_{control_version}_vs_{treatment_version}"

        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            description=description,
            control_version=control_version,
            treatment_version=treatment_version,
            traffic_allocation=traffic_allocation,
            target_sample_size=target_sample_size,
            max_duration_days=max_duration_days,
            min_success_rate_delta=min_success_rate_delta,
            max_cost_increase_pct=max_cost_increase_pct,
            status=ExperimentStatus.DRAFT,
            created_at=datetime.utcnow(),
            started_at=None,
            ended_at=None,
            created_by=created_by,
        )

        # Save to DynamoDB
        item = self._experiment_to_item(experiment)
        self.table.put_item(Item=item)

        logger.info(f"Created experiment: {experiment_id}")
        return experiment

    def start_experiment(self, experiment_id: str) -> bool:
        """
        Start running an experiment

        Args:
            experiment_id: Experiment to start

        Returns:
            True if started successfully
        """
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            logger.error(f"Experiment not found: {experiment_id}")
            return False

        if experiment.status != ExperimentStatus.DRAFT:
            logger.error(f"Cannot start experiment in status: {experiment.status}")
            return False

        self.table.update_item(
            Key={"experiment_id": experiment_id},
            UpdateExpression="SET #status = :status, started_at = :started_at",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":status": ExperimentStatus.RUNNING.value,
                ":started_at": datetime.utcnow().isoformat(),
            },
        )

        logger.info(f"Started experiment: {experiment_id}")
        return True

    def record_request(self, experiment_id: str, version: str):
        """
        Record that a request was handled by a specific version

        Args:
            experiment_id: Experiment ID
            version: Prompt version used (control or treatment)
        """
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            return

        # Increment counter
        field = (
            "control_requests"
            if version == experiment.control_version
            else "treatment_requests"
        )

        self.table.update_item(
            Key={"experiment_id": experiment_id},
            UpdateExpression=f"SET {field} = {field} + :inc",
            ExpressionAttributeValues={":inc": 1},
        )

    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """Get experiment by ID"""
        try:
            response = self.table.get_item(Key={"experiment_id": experiment_id})
            item = response.get("Item")
            if not item:
                return None
            return self._item_to_experiment(item)
        except Exception as e:
            logger.error(f"Failed to get experiment {experiment_id}: {e}")
            return None

    def list_experiments(
        self, status: Optional[ExperimentStatus] = None, limit: int = 50
    ) -> List[Experiment]:
        """List all experiments, optionally filtered by status"""
        try:
            if status:
                response = self.table.scan(
                    FilterExpression="#status = :status",
                    ExpressionAttributeNames={"#status": "status"},
                    ExpressionAttributeValues={":status": status.value},
                    Limit=limit,
                )
            else:
                response = self.table.scan(Limit=limit)

            items = response.get("Items", [])
            return [self._item_to_experiment(item) for item in items]
        except Exception as e:
            logger.error(f"Failed to list experiments: {e}")
            return []

    def complete_experiment(
        self, experiment_id: str, winner: str, conclusion: str
    ) -> bool:
        """
        Mark experiment as completed with results

        Args:
            experiment_id: Experiment ID
            winner: Winning version (control or treatment)
            conclusion: Summary of results

        Returns:
            True if updated successfully
        """
        try:
            self.table.update_item(
                Key={"experiment_id": experiment_id},
                UpdateExpression=(
                    "SET #status = :status, ended_at = :ended_at, "
                    "winner = :winner, conclusion = :conclusion"
                ),
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":status": ExperimentStatus.COMPLETED.value,
                    ":ended_at": datetime.utcnow().isoformat(),
                    ":winner": winner,
                    ":conclusion": conclusion,
                },
            )
            logger.info(f"Completed experiment {experiment_id}: winner = {winner}")
            return True
        except Exception as e:
            logger.error(f"Failed to complete experiment: {e}")
            return False

    def promote_treatment(self, experiment_id: str) -> bool:
        """Promote treatment version to production"""
        try:
            self.table.update_item(
                Key={"experiment_id": experiment_id},
                UpdateExpression="SET #status = :status",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={":status": ExperimentStatus.PROMOTED.value},
            )
            logger.info(f"Promoted treatment in experiment: {experiment_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to promote treatment: {e}")
            return False

    def _experiment_to_item(self, experiment: Experiment) -> Dict:
        """Convert Experiment to DynamoDB item"""
        item = asdict(experiment)
        item["created_at"] = experiment.created_at.isoformat()
        item["started_at"] = (
            experiment.started_at.isoformat() if experiment.started_at else None
        )
        item["ended_at"] = (
            experiment.ended_at.isoformat() if experiment.ended_at else None
        )
        item["status"] = experiment.status.value
        item["traffic_allocation"] = experiment.traffic_allocation.value
        return item

    def _item_to_experiment(self, item: Dict) -> Experiment:
        """Convert DynamoDB item to Experiment"""
        return Experiment(
            experiment_id=item["experiment_id"],
            name=item["name"],
            description=item["description"],
            control_version=item["control_version"],
            treatment_version=item["treatment_version"],
            traffic_allocation=TrafficAllocation(item["traffic_allocation"]),
            target_sample_size=int(item["target_sample_size"]),
            max_duration_days=int(item["max_duration_days"]),
            min_success_rate_delta=float(item["min_success_rate_delta"]),
            max_cost_increase_pct=float(item["max_cost_increase_pct"]),
            status=ExperimentStatus(item["status"]),
            created_at=datetime.fromisoformat(item["created_at"]),
            started_at=(
                datetime.fromisoformat(item["started_at"])
                if item.get("started_at")
                else None
            ),
            ended_at=(
                datetime.fromisoformat(item["ended_at"])
                if item.get("ended_at")
                else None
            ),
            created_by=item["created_by"],
            control_requests=int(item.get("control_requests", 0)),
            treatment_requests=int(item.get("treatment_requests", 0)),
            winner=item.get("winner"),
            conclusion=item.get("conclusion"),
        )
