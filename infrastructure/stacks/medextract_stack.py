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
    BundlingOptions,
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
        
        # Lambda functions for serverless API
        self.lambda_functions = self._create_lambda_functions()
        self.api_gateway = self._create_api_gateway()
        
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
                    f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-*",
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

    def _create_lambda_functions(self) -> Dict[str, lambda_.Function]:
        """Create Lambda functions for API backend"""
        functions = {}
        
        # Common environment variables
        common_env = {
            "DYNAMODB_TABLE": self.results_table.table_name,
            "EXPERIMENTS_TABLE": self.experiments_table.table_name,
            "S3_BUCKET": self.document_bucket.bucket_name,
            "ENVIRONMENT": self.env_name,
        }
        
        # Common bundling configuration for all Lambda functions
        # Bundles Python dependencies using Docker
        bundling_config = BundlingOptions(
            image=lambda_.Runtime.PYTHON_3_11.bundling_image,
            command=[
                "bash", "-c",
                "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output"
            ],
        )
        
        # 1. Upload Handler - Process document uploads
        functions["upload"] = lambda_.Function(
            self,
            "UploadFunction",
            function_name=f"medextract-upload-{self.env_name}",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda.handlers.upload.handler",
            code=lambda_.Code.from_asset("../backend", bundling=bundling_config),
            role=self.lambda_role,
            environment=common_env,
            memory_size=512,  # Low memory for simple S3 operations
            timeout=Duration.seconds(60),
            tracing=lambda_.Tracing.ACTIVE,  # X-Ray tracing
            log_retention=logs.RetentionDays.ONE_WEEK if self.env_name == "dev" else logs.RetentionDays.ONE_MONTH,
        )
        
        # 2. Extract Handler - Call Bedrock for data extraction
        functions["extract"] = lambda_.Function(
            self,
            "ExtractFunction",
            function_name=f"medextract-extract-{self.env_name}",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda.handlers.extract.handler",
            code=lambda_.Code.from_asset("../backend", bundling=bundling_config),
            role=self.lambda_role,
            environment=common_env,
            memory_size=self.config["lambda_memory"],  # Higher memory for ML inference
            timeout=Duration.seconds(300),  # 5 min for Bedrock calls
            tracing=lambda_.Tracing.ACTIVE,
            log_retention=logs.RetentionDays.ONE_WEEK if self.env_name == "dev" else logs.RetentionDays.ONE_MONTH,
            reserved_concurrent_executions=self.config.get("lambda_reserved_concurrency"),  # Cost control
        )
        
        # 3. Metrics Handler - Calculate MLOps metrics
        functions["metrics"] = lambda_.Function(
            self,
            "MetricsFunction",
            function_name=f"medextract-metrics-{self.env_name}",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda.handlers.metrics.handler",
            code=lambda_.Code.from_asset("../backend", bundling=bundling_config),
            role=self.lambda_role,
            environment=common_env,
            memory_size=1024,  # Medium memory for aggregations
            timeout=Duration.seconds(60),
            tracing=lambda_.Tracing.ACTIVE,
            log_retention=logs.RetentionDays.ONE_WEEK if self.env_name == "dev" else logs.RetentionDays.ONE_MONTH,
        )
        
        # 4. Experiment Handler - Manage A/B tests
        functions["experiment"] = lambda_.Function(
            self,
            "ExperimentFunction",
            function_name=f"medextract-experiment-{self.env_name}",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda.handlers.experiment.handler",
            code=lambda_.Code.from_asset("../backend", bundling=bundling_config),
            role=self.lambda_role,
            environment=common_env,
            memory_size=512,
            timeout=Duration.seconds(60),
            tracing=lambda_.Tracing.ACTIVE,
            log_retention=logs.RetentionDays.ONE_WEEK if self.env_name == "dev" else logs.RetentionDays.ONE_MONTH,
        )
        
        # Grant permissions to all functions
        for func in functions.values():
            self.document_bucket.grant_read_write(func)
            self.results_table.grant_read_write_data(func)
            self.experiments_table.grant_read_write_data(func)
        
        return functions

    def _create_api_gateway(self) -> apigw.RestApi:
        """Create API Gateway for Lambda functions"""
        api = apigw.RestApi(
            self,
            "MedExtractApi",
            rest_api_name=f"medextract-api-{self.env_name}",
            description="Serverless API for MedExtract platform",
            deploy_options=apigw.StageOptions(
                stage_name=self.env_name,
                tracing_enabled=True,  # X-Ray tracing
                # Logging disabled - requires CloudWatch Logs role setup in account
                # logging_level=apigw.MethodLoggingLevel.INFO,
                # data_trace_enabled=True,
                metrics_enabled=True,  # CloudWatch metrics
                throttling_rate_limit=100 if self.env_name == "prod" else 10,
                throttling_burst_limit=200 if self.env_name == "prod" else 20,
            ),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                allow_headers=["Content-Type", "Authorization"],
            ),
        )
        
        # Create API resources and integrate Lambda functions
        api_root = api.root.add_resource("api")
        
        # /api/upload
        upload_resource = api_root.add_resource("upload")
        upload_resource.add_method(
            "POST",
            apigw.LambdaIntegration(self.lambda_functions["upload"]),
        )
        
        # /api/extract/{document_id}
        extract_resource = api_root.add_resource("extract")
        extract_doc = extract_resource.add_resource("{document_id}")
        extract_doc.add_method(
            "POST",
            apigw.LambdaIntegration(self.lambda_functions["extract"]),
        )
        
        # /api/process/{document_id} (alias for extract)
        process_resource = api_root.add_resource("process")
        process_doc = process_resource.add_resource("{document_id}")
        process_doc.add_method(
            "POST",
            apigw.LambdaIntegration(self.lambda_functions["extract"]),
        )
        
        # /api/metrics/*
        metrics_resource = api_root.add_resource("metrics")
        metrics_resource.add_method(
            "GET",
            apigw.LambdaIntegration(self.lambda_functions["metrics"]),
        )
        metrics_prompts = metrics_resource.add_resource("prompts").add_resource("{version}")
        metrics_prompts.add_method(
            "GET",
            apigw.LambdaIntegration(self.lambda_functions["metrics"]),
        )
        
        # /api/metrics/compare
        metrics_compare = metrics_resource.add_resource("compare")
        metrics_compare.add_method(
            "POST",
            apigw.LambdaIntegration(self.lambda_functions["metrics"]),
        )
        metrics_compare.add_method("OPTIONS", apigw.MockIntegration(
            integration_responses=[{
                "statusCode": "200",
                "responseParameters": {
                    "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    "method.response.header.Access-Control-Allow-Origin": "'*'",
                    "method.response.header.Access-Control-Allow-Methods": "'POST,OPTIONS'"
                }
            }],
            passthrough_behavior=apigw.PassthroughBehavior.NEVER,
            request_templates={"application/json": '{"statusCode": 200}'}
        ), method_responses=[{
            "statusCode": "200",
            "responseParameters": {
                "method.response.header.Access-Control-Allow-Headers": True,
                "method.response.header.Access-Control-Allow-Origin": True,
                "method.response.header.Access-Control-Allow-Methods": True
            }
        }])
        
        # /api/experiments/*
        experiments_resource = api_root.add_resource("experiments")
        experiments_resource.add_method(
            "GET",
            apigw.LambdaIntegration(self.lambda_functions["experiment"]),
        )
        experiments_resource.add_method(
            "POST",
            apigw.LambdaIntegration(self.lambda_functions["experiment"]),
        )
        
        return api

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

        # Lambda function outputs
        CfnOutput(
            self,
            "UploadFunctionArn",
            value=self.lambda_functions["upload"].function_arn,
            description="Upload Lambda function ARN",
            export_name=f"MedExtract-{self.env_name}-UploadFunction",
        )

        CfnOutput(
            self,
            "ExtractFunctionArn",
            value=self.lambda_functions["extract"].function_arn,
            description="Extract Lambda function ARN",
            export_name=f"MedExtract-{self.env_name}-ExtractFunction",
        )

        # API Gateway output
        CfnOutput(
            self,
            "ApiGatewayUrl",
            value=self.api_gateway.url,
            description="API Gateway endpoint URL",
            export_name=f"MedExtract-{self.env_name}-ApiUrl",
        )

        if self.config.get("monitoring_alarms"):
            CfnOutput(
                self,
                "AlertTopicArn",
                value=self.alert_topic.topic_arn,
                description="SNS topic for CloudWatch alarms",
                export_name=f"MedExtract-{self.env_name}-AlertTopic",
            )
