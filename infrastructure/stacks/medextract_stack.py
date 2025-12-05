"""
MedExtract CDK Stack

Production infrastructure for medical document intelligence platform.
Includes: S3, DynamoDB, Lambda, IAM, CloudWatch, API Gateway
"""

from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    CfnOutput,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_sns as sns,
)
from constructs import Construct
from typing import Dict, Any


class MedExtractStack(Stack):
    """
    Complete infrastructure stack for MedExtract MLOps platform.
    
    Resources:
    - S3: Document storage with lifecycle policies
    - DynamoDB: Results and experiments storage
    - Lambda: API backend
    - IAM: Least-privilege roles
    - CloudWatch: Monitoring and alarms
    - SNS: Alerting
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_name: str,
        config: Dict[str, Any],
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.env_name = env_name
        self.config = config

        # Create resources
        self.document_bucket = self._create_s3_bucket()
        self.results_table = self._create_results_table()
        self.experiments_table = self._create_experiments_table()
        self.lambda_role = self._create_lambda_role()
        
        if config.get("monitoring_alarms"):
            self.alert_topic = self._create_alert_topic()
            self._create_cloudwatch_alarms()

        # Outputs
        self._create_outputs()

    def _create_s3_bucket(self) -> s3.Bucket:
        """Create S3 bucket for document storage"""
        bucket = s3.Bucket(
            self,
            "DocumentBucket",
            bucket_name=f"medextract-documents-{self.env_name}-{self.account}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldDocuments",
                    enabled=True,
                    expiration=Duration.days(self.config["s3_lifecycle_days"]),
                    noncurrent_version_expiration=Duration.days(7),
                ),
                s3.LifecycleRule(
                    id="TransitionToIA",
                    enabled=True,
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30),
                        )
                    ],
                ),
            ],
            removal_policy=RemovalPolicy.RETAIN if self.config["enable_deletion_protection"] else RemovalPolicy.DESTROY,
            auto_delete_objects=not self.config["enable_deletion_protection"],
        )

        # Add CORS for frontend uploads
        bucket.add_cors_rule(
            allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT, s3.HttpMethods.POST],
            allowed_origins=["http://localhost:3000", "http://localhost:5173"],
            allowed_headers=["*"],
            max_age=3000,
        )

        return bucket

    def _create_results_table(self) -> dynamodb.Table:
        """Create DynamoDB table for extraction results"""
        
        if self.config["dynamodb_billing_mode"] == "PROVISIONED":
            billing_mode = dynamodb.BillingMode.PROVISIONED
            read_capacity = self.config.get("dynamodb_read_capacity", 5)
            write_capacity = self.config.get("dynamodb_write_capacity", 5)
        else:
            billing_mode = dynamodb.BillingMode.PAY_PER_REQUEST
            read_capacity = None
            write_capacity = None

        table = dynamodb.Table(
            self,
            "ResultsTable",
            table_name=f"medextract-results-{self.env_name}",
            partition_key=dynamodb.Attribute(
                name="document_id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=billing_mode,
            read_capacity=read_capacity,
            write_capacity=write_capacity,
            point_in_time_recovery=self.config.get("enable_deletion_protection", False),
            removal_policy=RemovalPolicy.RETAIN if self.config["enable_deletion_protection"] else RemovalPolicy.DESTROY,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,  # For analytics
        )

        # Global Secondary Index for querying by upload time
        table.add_global_secondary_index(
            index_name="UploadedAtIndex",
            partition_key=dynamodb.Attribute(
                name="uploaded_at", type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        # GSI for querying by prompt version (MLOps)
        table.add_global_secondary_index(
            index_name="PromptVersionIndex",
            partition_key=dynamodb.Attribute(
                name="prompt_version", type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        return table

    def _create_experiments_table(self) -> dynamodb.Table:
        """Create DynamoDB table for A/B experiments"""
        
        billing_mode = (
            dynamodb.BillingMode.PROVISIONED
            if self.config["dynamodb_billing_mode"] == "PROVISIONED"
            else dynamodb.BillingMode.PAY_PER_REQUEST
        )

        table = dynamodb.Table(
            self,
            "ExperimentsTable",
            table_name=f"medextract-experiments-{self.env_name}",
            partition_key=dynamodb.Attribute(
                name="experiment_id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=billing_mode,
            point_in_time_recovery=self.config.get("enable_deletion_protection", False),
            removal_policy=RemovalPolicy.RETAIN if self.config["enable_deletion_protection"] else RemovalPolicy.DESTROY,
        )

        # GSI for querying by status
        table.add_global_secondary_index(
            index_name="StatusIndex",
            partition_key=dynamodb.Attribute(
                name="status", type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        return table

    def _create_lambda_role(self) -> iam.Role:
        """Create IAM role for Lambda with least-privilege permissions"""
        
        role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Execution role for MedExtract Lambda functions",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
            ],
        )

        # S3 permissions (scoped to our bucket)
        self.document_bucket.grant_read_write(role)

        # DynamoDB permissions
        self.results_table.grant_read_write_data(role)
        self.experiments_table.grant_read_write_data(role)

        # Bedrock permissions (specific to Claude models)
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=[
                    f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-3-haiku-*",
                    f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-3-sonnet-*",
                ],
            )
        )

        # CloudWatch Logs (explicit for custom log groups)
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                resources=[f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws/lambda/medextract-*"],
            )
        )

        return role

    def _create_alert_topic(self) -> sns.Topic:
        """Create SNS topic for CloudWatch alarms"""
        topic = sns.Topic(
            self,
            "AlertTopic",
            topic_name=f"medextract-alerts-{self.env_name}",
            display_name=f"MedExtract Alerts ({self.env_name})",
        )
        return topic

    def _create_cloudwatch_alarms(self):
        """Create CloudWatch alarms for monitoring"""
        
        # DynamoDB Read/Write Capacity Alarms (for provisioned mode)
        if self.config["dynamodb_billing_mode"] == "PROVISIONED":
            # Results table read capacity alarm
            cloudwatch.Alarm(
                self,
                "ResultsTableReadCapacityAlarm",
                alarm_name=f"medextract-results-read-capacity-{self.env_name}",
                metric=self.results_table.metric_consumed_read_capacity_units(
                    statistic="Average", period=Duration.minutes(5)
                ),
                threshold=self.config.get("dynamodb_read_capacity", 5) * 0.8,  # 80% threshold
                evaluation_periods=2,
                alarm_description="Results table read capacity approaching limit",
            ).add_alarm_action(cw_actions.SnsAction(self.alert_topic))

            # Results table write capacity alarm
            cloudwatch.Alarm(
                self,
                "ResultsTableWriteCapacityAlarm",
                alarm_name=f"medextract-results-write-capacity-{self.env_name}",
                metric=self.results_table.metric_consumed_write_capacity_units(
                    statistic="Average", period=Duration.minutes(5)
                ),
                threshold=self.config.get("dynamodb_write_capacity", 5) * 0.8,
                evaluation_periods=2,
                alarm_description="Results table write capacity approaching limit",
            ).add_alarm_action(cw_actions.SnsAction(self.alert_topic))

        # S3 bucket size alarm (cost monitoring)
        bucket_size_metric = cloudwatch.Metric(
            namespace="AWS/S3",
            metric_name="BucketSizeBytes",
            dimensions_map={
                "BucketName": self.document_bucket.bucket_name,
                "StorageType": "StandardStorage",
            },
            statistic="Average",
            period=Duration.days(1),
        )

        cloudwatch.Alarm(
            self,
            "S3BucketSizeAlarm",
            alarm_name=f"medextract-s3-size-{self.env_name}",
            metric=bucket_size_metric,
            threshold=100 * 1024 * 1024 * 1024,  # 100 GB
            evaluation_periods=1,
            alarm_description="S3 bucket size exceeded 100 GB",
        ).add_alarm_action(cw_actions.SnsAction(self.alert_topic))

    def _create_outputs(self):
        """Create CloudFormation outputs"""
        
        CfnOutput(
            self,
            "DocumentBucketName",
            value=self.document_bucket.bucket_name,
            description="S3 bucket for document storage",
            export_name=f"MedExtract-{self.env_name}-DocumentBucket",
        )

        CfnOutput(
            self,
            "ResultsTableName",
            value=self.results_table.table_name,
            description="DynamoDB table for extraction results",
            export_name=f"MedExtract-{self.env_name}-ResultsTable",
        )

        CfnOutput(
            self,
            "ExperimentsTableName",
            value=self.experiments_table.table_name,
            description="DynamoDB table for A/B experiments",
            export_name=f"MedExtract-{self.env_name}-ExperimentsTable",
        )

        CfnOutput(
            self,
            "LambdaRoleArn",
            value=self.lambda_role.role_arn,
            description="IAM role for Lambda execution",
            export_name=f"MedExtract-{self.env_name}-LambdaRole",
        )

        if self.config.get("monitoring_alarms"):
            CfnOutput(
                self,
                "AlertTopicArn",
                value=self.alert_topic.topic_arn,
                description="SNS topic for CloudWatch alarms",
                export_name=f"MedExtract-{self.env_name}-AlertTopic",
            )
