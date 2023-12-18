import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_cdk.assertions import Match
from code.code_stack import CodeStack


STACK = CodeStack(core.App(context={
    "logging": {
        "lambda_log_level": "INFO",
        "streamlit_log_level": "INFO"
    },
}), "code", )


def test_s3_bucket_created():
    template = assertions.Template.from_stack(STACK)

    template.resource_count_is("AWS::S3::Bucket", 2)
    template.has_resource_properties("AWS::S3::Bucket", {
        "BucketName": {"Fn::Join": ["", [Match.any_value(), "-sagemaker-pricing-", Match.any_value()]]}
    })
    template.has_resource_properties("AWS::S3::Bucket", {
        "BucketName": {"Fn::Join": ["", [Match.any_value(), "-kendra-data-source-", Match.any_value()]]}
    })


def test_kms_created():
    template = assertions.Template.from_stack(STACK)

    template.resource_count_is("AWS::KMS::Key", 1)
    template.has_resource_properties("AWS::KMS::Alias", {
        "AliasName": {"Fn::Join": ["", ["alias/", Match.any_value(), "/genai_key"]]}
    })


def test_kendra_index_created():
    template = assertions.Template.from_stack(STACK)

    template.resource_count_is("AWS::KMS::Key", 1)
    template.resource_count_is("AWS::Kendra::DataSource", 1)
    template.has_resource_properties("AWS::Kendra::Index", Match.object_like({
        "Edition": "DEVELOPER_EDITION"
    }))
    template.has_resource_properties("AWS::Kendra::DataSource", Match.object_like({
        "DataSourceConfiguration": {"S3Configuration": {"BucketName": Match.any_value()}}
    }))


def test_lambda_created():
    template = assertions.Template.from_stack(STACK)

    template.has_resource_properties("AWS::Lambda::Function", Match.object_like({
        "MemorySize": 2048,
        "PackageType": "Image",
        "Timeout": 900,
        "Architectures": ["arm64"],
        "FunctionName": {"Fn::Join": ["", [Match.any_value(), "-chatbot-lambda"]]}
    }))


def test_database_created():
    template = assertions.Template.from_stack(STACK)

    template.resource_count_is("AWS::Glue::Database", 1)
    template.resource_count_is("AWS::Glue::Crawler", 1)
    template.has_resource_properties("AWS::Glue::Database", Match.object_like({
        "DatabaseInput": {"Name": {"Fn::Join": ["", [Match.any_value(), "-pricing-db"]]}}
    }))
    template.has_resource_properties("AWS::Glue::Crawler", Match.object_like({
        "Name": {"Fn::Join": ["", [Match.any_value(), "-sagemaker-pricing-crawler"]]}
    }))


def test_streamlit_app_created():
    template = assertions.Template.from_stack(STACK)

    template.resource_count_is("AWS::ECS::Service", 1)
    template.resource_count_is("AWS::ECS::TaskDefinition", 1)
    template.resource_count_is("AWS::ElasticLoadBalancingV2::Listener", 1)
    template.has_resource_properties("AWS::ECS::TaskDefinition", Match.object_like({
        "ContainerDefinitions": [{"PortMappings": [{"ContainerPort": 8501, "Protocol": "tcp"}]}]
    }))
    template.has_resource_properties("AWS::ElasticLoadBalancingV2::Listener", Match.object_like({
        "Port": 80, "Protocol": "HTTP"
    }))
