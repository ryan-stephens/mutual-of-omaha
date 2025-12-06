"""
Lambda handler for experiment operations
"""

import logging
import sys
import os

sys.path.insert(0, "/opt/python")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    create_response,
    create_error_response,
    parse_event_body,
    get_path_parameter,
)
from app.services.experiment_service import ExperimentService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

experiment_service = ExperimentService()


def handler(event, context):
    """
    Process experiment requests

    Supports:
    - GET /experiments - List all experiments
    - GET /experiments/{id} - Get experiment details
    - POST /experiments - Create new experiment
    - PUT /experiments/{id} - Update experiment
    """
    try:
        http_method = event.get("httpMethod", "GET")
        experiment_id = get_path_parameter(event, "experiment_id")

        if http_method == "GET":
            if experiment_id:
                logger.info(f"Getting experiment: {experiment_id}")
                experiment = experiment_service.get_experiment(experiment_id)

                if not experiment:
                    return create_error_response(404, f"Experiment not found: {experiment_id}")

                return create_response(
                    200,
                    {
                        "experiment_id": experiment.experiment_id,
                        "name": experiment.name,
                        "description": experiment.description,
                        "status": experiment.status.value,
                        "control_version": experiment.control_version,
                        "treatment_version": experiment.treatment_version,
                        "traffic_allocation": {
                            "control": experiment.traffic_allocation.control_pct,
                            "treatment": experiment.traffic_allocation.treatment_pct,
                        },
                        "created_at": experiment.created_at,
                        "started_at": experiment.started_at,
                        "ended_at": experiment.ended_at,
                    },
                )
            else:
                logger.info("Listing all experiments")
                experiments = experiment_service.list_experiments()

                experiments_list = []
                for exp in experiments:
                    experiments_list.append(
                        {
                            "experiment_id": exp.experiment_id,
                            "name": exp.name,
                            "status": exp.status.value,
                            "control_version": exp.control_version,
                            "treatment_version": exp.treatment_version,
                            "created_at": exp.created_at,
                        }
                    )

                return create_response(
                    200,
                    {"experiments": experiments_list, "count": len(experiments_list)},
                )

        elif http_method == "POST":
            body = parse_event_body(event)

            required_fields = [
                "name",
                "description",
                "control_version",
                "treatment_version",
            ]
            for field in required_fields:
                if field not in body:
                    return create_error_response(400, f"Missing required field: {field}")

            logger.info(f"Creating experiment: {body['name']}")

            experiment = experiment_service.create_experiment(
                name=body["name"],
                description=body["description"],
                control_version=body["control_version"],
                treatment_version=body["treatment_version"],
                control_pct=body.get("control_pct", 50),
                treatment_pct=body.get("treatment_pct", 50),
            )

            return create_response(
                201,
                {
                    "experiment_id": experiment.experiment_id,
                    "name": experiment.name,
                    "status": experiment.status.value,
                    "message": "Experiment created successfully",
                },
            )

        elif http_method == "PUT":
            if not experiment_id:
                return create_error_response(400, "Missing experiment_id")

            body = parse_event_body(event)
            action = body.get("action")

            if action == "start":
                logger.info(f"Starting experiment: {experiment_id}")
                success = experiment_service.start_experiment(experiment_id)
                if success:
                    return create_response(200, {"message": "Experiment started"})
                else:
                    return create_error_response(500, "Failed to start experiment")

            elif action == "complete":
                logger.info(f"Completing experiment: {experiment_id}")
                winner = body.get("winner")
                conclusion = body.get("conclusion", "")

                if not winner:
                    return create_error_response(400, "Missing 'winner' field")

                success = experiment_service.complete_experiment(experiment_id, winner, conclusion)

                if success:
                    return create_response(200, {"message": "Experiment completed"})
                else:
                    return create_error_response(500, "Failed to complete experiment")

            else:
                return create_error_response(400, f"Unknown action: {action}")

        else:
            return create_error_response(405, f"Method not allowed: {http_method}")

    except Exception as e:
        logger.error(f"Experiment handler error: {e}", exc_info=True)
        return create_error_response(500, f"Failed to process experiment request: {str(e)}")
