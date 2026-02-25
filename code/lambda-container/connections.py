import os
import boto3
from langchain_aws import ChatBedrock


class Connections:
    region_name = os.environ["AWS_REGION"]
    s3_rawdata_bucket_name = os.environ["DATA_SOURCE_BUCKET_NAME"]
    s3_pricing_bucket_name = os.environ["PRICING_DATA_SOURCE_BUCKET_NAME"]
    kendra_rawdata_index_id = os.environ["KENDRA_INDEX_ID"]
    sagemaker_pricing_database = os.environ["SAGEMAKER_PRICING_DATABASE"]
    log_level = os.environ["LOG_LEVEL"]
    kendra_client = boto3.client("kendra", region_name=region_name)
    s3_resource = boto3.resource("s3", region_name=region_name)
    bedrock_client = boto3.client("bedrock-runtime", region_name=region_name)

    MODELID_MAPPING = {
        "ClaudeHaiku": "global.anthropic.claude-haiku-4-5-20251001-v1:0",
        "ClaudeSonnet": "global.anthropic.claude-sonnet-4-6",
        "ClaudeOpus": "global.anthropic.claude-opus-4-6-v1",
    }

    @staticmethod
    def get_bedrock_llm(model_name="ClaudeSonnet", max_tokens=256, cache=False):
        model_id = Connections.MODELID_MAPPING.get(
            model_name, Connections.MODELID_MAPPING["ClaudeSonnet"]
        )
        llm = ChatBedrock(
            client=Connections.bedrock_client,
            model_id=model_id,
            model_kwargs={
                "max_tokens": max_tokens,
                "temperature": 0,
                "top_p": 1,
                "top_k": 50,
            },
            cache=cache,
        )
        return llm
