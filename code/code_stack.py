import os
import os.path as path
from aws_cdk import (
    Duration,
    Stack,
    Aws,
    RemovalPolicy,
    CfnOutput,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_kms as kms,
    aws_iam as iam,
    aws_s3 as s3,
    aws_kendra as kendra,
    aws_glue as glue,
    aws_lambda as lambda_,
    aws_s3_deployment as s3deploy,
    aws_ecs_patterns as ecs_patterns,
)
from constructs import Construct
from aws_cdk.aws_ecr_assets import Platform
from cdk_nag import NagSuppressions

SAGEMAKER_PRICING_DESTINATION_PREFIX = "source_data"
ASSETS_FOLDER_NAME = "assets"


class CodeStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        logging_context = dict(self.node.try_get_context("logging"))
        kms_key = self.create_kms_key()
        kendra_bucket, sagemaker_bucket = self.create_data_source_bucket(
            kms_key)
        kendra_index = self.create_kendra_index(kendra_bucket, kms_key)
        self.upload_files_to_s3(kendra_bucket, sagemaker_bucket, kms_key)
        glue_database, _ = self.create_glue_database(sagemaker_bucket, kms_key)
        lambda_function = self.create_lambda_function(
            kendra_index, kendra_bucket, sagemaker_bucket, kms_key, glue_database, logging_context
        )
        self.create_streamlit_app(lambda_function, logging_context)

    def create_kms_key(self):
        # Creating new KMS key and confgiure it for S3 object encryption
        kms_key = kms.Key(
            self,
            "KMSKey",
            alias=f"alias/{Aws.STACK_NAME}/genai_key",
            enable_key_rotation=True,
            pending_window=Duration.days(7),
            removal_policy=RemovalPolicy.DESTROY,
        )
        kms_key.grant_encrypt_decrypt(
            iam.AnyPrincipal().with_conditions(
                {
                    "StringEquals": {
                        "kms:CallerAccount": f"{Aws.ACCOUNT_ID}",
                        "kms:ViaService": f"s3.{Aws.REGION}.amazonaws.com",
                    },
                }
            )
        )
        kms_key.grant_encrypt_decrypt(
            iam.AnyPrincipal().with_conditions(
                {
                    "StringEquals": {
                        "kms:CallerAccount": f"{Aws.ACCOUNT_ID}",
                        "kms:ViaService": f"kendra.{Aws.REGION}.amazonaws.com",
                    },
                }
            )
        )
        kms_key.grant_encrypt_decrypt(
            iam.ServicePrincipal("kendra.amazonaws.com"))
        kms_key.grant_encrypt_decrypt(
            iam.ServicePrincipal(f"logs.{Aws.REGION}.amazonaws.com")
        )

        return kms_key

    def create_data_source_bucket(self, kms_key):
        # creating kendra source bucket
        kendra_bucket = s3.Bucket(
            self,
            "SourceBucket",
            bucket_name=f"{Aws.STACK_NAME}-kendra-data-source-{Aws.ACCOUNT_ID}",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=kms_key,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
        )
        NagSuppressions.add_resource_suppressions(
            kendra_bucket,
            suppressions=[
                {
                    "id": "AwsSolutions-S1",
                    "reason": "Demo app hence server access logs not enabled",
                }
            ],
        )
        CfnOutput(self, "KendraSourceBucket", value=kendra_bucket.bucket_name)

        # creating kendra source bucket
        sagemaker_bucket = s3.Bucket(
            self,
            "SagemakerPricingBucket",
            bucket_name=f"{Aws.STACK_NAME}-sagemaker-pricing-{Aws.ACCOUNT_ID}",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=kms_key,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
        )
        NagSuppressions.add_resource_suppressions(
            sagemaker_bucket,
            suppressions=[
                {
                    "id": "AwsSolutions-S1",
                    "reason": "Demo app hence server access logs not enabled",
                }
            ],
        )
        CfnOutput(self, "PricingBucket", value=sagemaker_bucket.bucket_name)
        return kendra_bucket, sagemaker_bucket

    def create_kendra_index(self, bucket, kms_key):
        # Create IAM role for Kendra index
        kendra_index_role = iam.Role(
            self,
            "KendraIndexRole",
            assumed_by=iam.ServicePrincipal("kendra.amazonaws.com"),
        )
        # Add Cloudwatch policy to Kendra index role for logs access
        kendra_index_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[
                    f"arn:aws:logs:{Aws.REGION}:{Aws.ACCOUNT_ID}:log-group:/aws/kendra/*"
                ],
                actions=["logs:CreateLogGroup"],
            )
        )
        kendra_index_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=["*"],
                actions=["cloudwatch:PutMetricData"],
                conditions={"StringEquals": {
                    "cloudwatch:namespace": "AWS/Kendra"}},
            )
        )
        kendra_index_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[
                    f"arn:aws:logs:{Aws.REGION}:{Aws.ACCOUNT_ID}:log-group:/aws/kendra/*:log-stream:*"
                ],
                actions=[
                    "logs:DescribeLogStreams",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
            )
        )

        # creating Kendra index
        index = kendra.CfnIndex(
            self,
            "KendraIndex",
            name=f"{Aws.STACK_NAME}-chatbot-index",
            role_arn=kendra_index_role.role_arn,
            edition="DEVELOPER_EDITION",
            description="Kendra index for GenAI Chatbot",
            user_context_policy="ATTRIBUTE_FILTER",
            server_side_encryption_configuration=kendra.CfnIndex.ServerSideEncryptionConfigurationProperty(
                kms_key_id=kms_key.key_id
            ),
        )

        index_data_source = self.create_kendra_index_source(
            index, bucket, kms_key)
        CfnOutput(self, "KendraIndexId", value=index.ref)
        CfnOutput(self, "KendraIndexDataSourceName",
                  value=index_data_source.name)
        return index

    def create_kendra_index_source(self, kendra_index, bucket, kms_key):
        # Create IAM role for Kendra index
        data_source_role = iam.Role(
            self,
            "KendraDataSourceRole",
            assumed_by=iam.ServicePrincipal("kendra.amazonaws.com"),
        )

        bucket.grant_read(data_source_role)
        kms_key.grant_encrypt_decrypt(data_source_role)
        data_source_role.add_to_policy(
            iam.PolicyStatement.from_json(
                {
                    "Effect": "Allow",
                    "Action": ["kendra:BatchPutDocument", "kendra:BatchDeleteDocument"],
                    "Resource": [kendra_index.attr_arn],
                }
            )
        )

        # creating Kendra index data source
        index_data_source = kendra.CfnDataSource(
            self,
            "KendraIndexDataSource",
            name=f"{Aws.STACK_NAME}-chatbot-index",
            index_id=kendra_index.ref,
            type="S3",
            data_source_configuration=kendra.CfnDataSource.DataSourceConfigurationProperty(
                s3_configuration=kendra.CfnDataSource.S3DataSourceConfigurationProperty(
                    bucket_name=bucket.bucket_name,
                )
            ),
            role_arn=data_source_role.role_arn,
        )
        return index_data_source

    def upload_files_to_s3(self, kendra_bucket, sagemaker_bucket, kms_key):
        # Uploading files to S3 bucket
        s3deploy.BucketDeployment(
            self,
            "KendraDocumentDeployment",
            sources=[
                s3deploy.Source.asset(
                    path.join(os.getcwd(), ASSETS_FOLDER_NAME,
                              "kendra_documents/sm_dg.zip")
                )
            ],
            destination_bucket=kendra_bucket,
            retain_on_delete=False,
        )

        s3deploy.BucketDeployment(
            self,
            "SagemakerPricingDeployment",
            sources=[
                s3deploy.Source.asset(
                    path.join(os.getcwd(), ASSETS_FOLDER_NAME,
                              "sagemaker_source")
                )
            ],
            destination_bucket=sagemaker_bucket,
            retain_on_delete=False,
            destination_key_prefix=SAGEMAKER_PRICING_DESTINATION_PREFIX,
        )
        return

    def create_glue_database(self, sagemaker_bucket, kms_key):
        # Create IAM role for Glue Crawlers
        glue_role = iam.Role(
            self,
            "GlueRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                )
            ],
        )
        sagemaker_bucket.grant_read(glue_role)
        kms_key.grant_encrypt_decrypt(glue_role)
        glue_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=["*"],
                actions=["logs:AssociateKmsKey"],
            )
        )
        # # Create Glue database
        glue_database = glue.CfnDatabase(
            self,
            "SagemakerPricingDatabase",
            catalog_id=Aws.ACCOUNT_ID,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name=f"{Aws.STACK_NAME}-pricing-db"
            ),
        )

        cfn_security_configuration = glue.CfnSecurityConfiguration(
            self,
            "SecurityConfiguration",
            encryption_configuration=glue.CfnSecurityConfiguration.EncryptionConfigurationProperty(
                cloud_watch_encryption=glue.CfnSecurityConfiguration.CloudWatchEncryptionProperty(
                    cloud_watch_encryption_mode="SSE-KMS", kms_key_arn=kms_key.key_arn
                ),
                s3_encryptions=[
                    glue.CfnSecurityConfiguration.S3EncryptionProperty(
                        kms_key_arn=kms_key.key_arn, s3_encryption_mode="SSE-KMS"
                    )
                ],
            ),
            name=f"{Aws.STACK_NAME}-security-config",
        )

        cfn_crawler = glue.CfnCrawler(
            self,
            "SagemakerPricingCrawler",
            role=glue_role.role_name,
            crawler_security_configuration=cfn_security_configuration.name,
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[
                    glue.CfnCrawler.S3TargetProperty(
                        path=f"s3://{sagemaker_bucket.bucket_name}/{SAGEMAKER_PRICING_DESTINATION_PREFIX}/asynchronous_inference_price/",
                    ),
                    glue.CfnCrawler.S3TargetProperty(
                        path=f"s3://{sagemaker_bucket.bucket_name}/{SAGEMAKER_PRICING_DESTINATION_PREFIX}/inference_accelerator_price/",
                    ),
                    glue.CfnCrawler.S3TargetProperty(
                        path=f"s3://{sagemaker_bucket.bucket_name}/{SAGEMAKER_PRICING_DESTINATION_PREFIX}/real_time_inference_price/",
                    ),
                    glue.CfnCrawler.S3TargetProperty(
                        path=f"s3://{sagemaker_bucket.bucket_name}/{SAGEMAKER_PRICING_DESTINATION_PREFIX}/training_price/",
                    ),
                ]
            ),
            database_name=glue_database.ref,
            description="Crawler job for Sagemaker pricing",
            name=f"{Aws.STACK_NAME}-sagemaker-pricing-crawler",
        )
        NagSuppressions.add_resource_suppressions(
            cfn_crawler,
            suppressions=[
                {
                    "id": "AwsSolutions-GL1",
                    "reason": "Logs encryption enabled for the crawler. False positive warning",
                }
            ],
        )

        return glue_database, cfn_crawler

    def create_lambda_function(self, kendra_index, kendra_bucket, sagemaker_bucket, kms_key, glue_database, logging_context):
        # Create AWS Lambda function
        ecr_image = lambda_.EcrImageCode.from_asset_image(
            directory=path.join(os.getcwd(), "code", "lambda-container"),
            platform=Platform.LINUX_ARM64,
        )

        # Create IAM role for Lambda function
        lambda_role = iam.Role(
            self,
            "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                # Add a managed policy for Amazon Kendra
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonKendraReadOnlyAccess"
                ),
                # Add a managed policy for Amazon Athena AmazonBedrockFullAccess
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonAthenaFullAccess"
                ),
                # Add a managed policy for AmazonBedrockFullAccess
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonBedrockFullAccess"
                ),
            ],
        )

        lambda_function = lambda_.Function(
            self,
            "LambdaFunction",
            function_name=f"{Aws.STACK_NAME}-chatbot-lambda",
            description="Lambda code for GenAI Chatbot",
            architecture=lambda_.Architecture.ARM_64,
            handler=lambda_.Handler.FROM_IMAGE,
            runtime=lambda_.Runtime.FROM_IMAGE,
            code=ecr_image,
            environment={
                "KENDRA_INDEX_ID": kendra_index.ref,
                "DATA_SOURCE_BUCKET_NAME": kendra_bucket.bucket_name,
                "PRICING_DATA_SOURCE_BUCKET_NAME": sagemaker_bucket.bucket_name,
                "SAGEMAKER_PRICING_DATABASE": glue_database.ref,
                "LOG_LEVEL": logging_context["lambda_log_level"],
            },
            environment_encryption=kms_key,
            role=lambda_role,
            timeout=Duration.minutes(15),
            memory_size=2048,
        )

        sagemaker_bucket.grant_read_write(lambda_role)
        kendra_bucket.grant_read_write(lambda_role)
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[kendra_index.attr_arn],
                actions=["kendra:Retrieve"],
            )
        )

        CfnOutput(self, "LambdaName", value=lambda_function.function_name)
        return lambda_function

    def create_streamlit_app(self, lambda_function, logging_context):
        # Create a VPC
        vpc = ec2.Vpc(
            self, "ChatBotDemoVPC", max_azs=2, vpc_name=f"{Aws.STACK_NAME}-vpc"
        )
        NagSuppressions.add_resource_suppressions(
            vpc,
            suppressions=[
                {"id": "AwsSolutions-VPC7", "reason": "VPC used for hosting demo app"}
            ],
        )

        # Create ECS cluster
        cluster = ecs.Cluster(
            self,
            "ChatBotDemoCluster",
            cluster_name=f"{Aws.STACK_NAME}-ecs-cluster",
            container_insights=True,
            vpc=vpc,
        )

        # Build Dockerfile from local folder and push to ECR
        image = ecs.ContainerImage.from_asset(
            path.join(os.getcwd(), "code", "streamlit-app"),
            platform=Platform.LINUX_ARM64,
        )

        #  Create Fargate service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "ChatBotService",
            cluster=cluster,
            cpu=2048,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image,
                container_port=8501,
                environment={
                    "LAMBDA_FUNCTION_NAME": lambda_function.function_name,
                    "LAMBDA_FUNCTION_ARN": lambda_function.function_arn,
                    "LOG_LEVEL": logging_context["streamlit_log_level"],
                },
            ),
            service_name=f"{Aws.STACK_NAME}-chatbot-service",
            memory_limit_mib=4096,
            public_load_balancer=True,
            platform_version=ecs.FargatePlatformVersion.LATEST,
            runtime_platform=ecs.RuntimePlatform(
                operating_system_family=ecs.OperatingSystemFamily.LINUX,
                cpu_architecture=ecs.CpuArchitecture.ARM64,
            ),
        )
        NagSuppressions.add_resource_suppressions(
            fargate_service,
            suppressions=[
                {"id": "AwsSolutions-ELB2", "reason": "LB used for hosting demo app"}
            ],
            apply_to_children=True,
        )
        NagSuppressions.add_resource_suppressions(
            fargate_service,
            suppressions=[
                {
                    "id": "AwsSolutions-EC23",
                    "reason": "Enabling Chatbot access in HTTP port",
                }
            ],
            apply_to_children=True,
        )
        NagSuppressions.add_resource_suppressions(
            fargate_service,
            suppressions=[
                {
                    "id": "AwsSolutions-ECS2",
                    "reason": "Environment variables needed for accessing lambda",
                }
            ],
            apply_to_children=True,
        )

        # Add policies to task role
        lambda_function.grant_invoke(fargate_service.task_definition.task_role)

        # Setup task auto-scaling
        scaling = fargate_service.service.auto_scale_task_count(max_capacity=3)
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=50,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )
        return fargate_service
