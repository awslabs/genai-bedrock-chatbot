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
        "ClaudeSonnet": "global.anthropic.claude-sonnet-5",
        "ClaudeOpus": "global.anthropic.claude-opus-4-8",
    }

    # Claude Sonnet 5 and Claude Opus 4.8 deprecated the sampling parameters
    # (temperature, top_p, top_k). Passing any of them raises a
    # ValidationException on both InvokeModel and Converse. Earlier models such
    # as Claude Haiku 4.5 still accept temperature, but reject temperature and
    # top_p together, so top_p/top_k are no longer sent at all.
    MODELS_WITHOUT_SAMPLING_PARAMS = frozenset(
        {
            "global.anthropic.claude-sonnet-5",
            "global.anthropic.claude-opus-4-8",
        }
    )

    @staticmethod
    def supports_sampling_params(model_id):
        """Whether the given Bedrock model accepts temperature/top_p/top_k."""
        return model_id not in Connections.MODELS_WITHOUT_SAMPLING_PARAMS

    @staticmethod
    def get_bedrock_llm(model_name="ClaudeSonnet", max_tokens=256, cache=False):
        model_id = Connections.MODELID_MAPPING.get(
            model_name, Connections.MODELID_MAPPING["ClaudeSonnet"]
        )
        model_kwargs = {"max_tokens": max_tokens}
        if Connections.supports_sampling_params(model_id):
            model_kwargs["temperature"] = 0
        llm = ChatBedrock(
            client=Connections.bedrock_client,
            model_id=model_id,
            model_kwargs=model_kwargs,
            cache=cache,
        )
        return llm
