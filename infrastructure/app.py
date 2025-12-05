#!/usr/bin/env python3
"""
AWS CDK Application Entry Point

Defines the infrastructure stack for MedExtract MLOps platform.
Supports multiple environments (dev, staging, prod) with appropriate configurations.
"""

import os
from aws_cdk import App, Environment, Tags

from stacks.medextract_stack import MedExtractStack

app = App()

# Get environment from context or default to 'dev'
env_name = app.node.try_get_context("env") or "dev"

# AWS Account and Region from environment variables or CDK defaults
account = os.environ.get("CDK_DEFAULT_ACCOUNT")
region = os.environ.get("CDK_DEFAULT_REGION", "us-east-1")

# Environment-specific configurations
env_config = {
    "dev": {
        "dynamodb_billing_mode": "PAY_PER_REQUEST",
        "s3_lifecycle_days": 30,
        "enable_deletion_protection": False,
        "lambda_memory_mb": 512,
        "api_throttle_rate": 100,
        "api_throttle_burst": 200,
        "monitoring_alarms": False,
    },
    "staging": {
        "dynamodb_billing_mode": "PAY_PER_REQUEST",
        "s3_lifecycle_days": 90,
        "enable_deletion_protection": True,
        "lambda_memory_mb": 1024,
        "api_throttle_rate": 500,
        "api_throttle_burst": 1000,
        "monitoring_alarms": True,
    },
    "prod": {
        "dynamodb_billing_mode": "PROVISIONED",
        "dynamodb_read_capacity": 10,
        "dynamodb_write_capacity": 5,
        "s3_lifecycle_days": 365,
        "enable_deletion_protection": True,
        "lambda_memory_mb": 2048,
        "api_throttle_rate": 1000,
        "api_throttle_burst": 2000,
        "monitoring_alarms": True,
        "backup_enabled": True,
    },
}

# Create the stack
stack = MedExtractStack(
    app,
    f"MedExtractStack-{env_name}",
    env=Environment(account=account, region=region),
    env_name=env_name,
    config=env_config[env_name],
    description=f"MedExtract MLOps Platform - {env_name.upper()} environment",
)

# Add tags for cost tracking and organization
Tags.of(stack).add("Project", "MedExtract")
Tags.of(stack).add("Environment", env_name)
Tags.of(stack).add("ManagedBy", "CDK")
Tags.of(stack).add("CostCenter", "AI-ML")

app.synth()
