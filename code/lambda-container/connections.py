import os
import boto3
from langchain_community.llms import Bedrock


class Connections:
    region_name = os.environ['AWS_REGION']
    s3_rawdata_bucket_name = os.environ['DATA_SOURCE_BUCKET_NAME']
    s3_pricing_bucket_name = os.environ['PRICING_DATA_SOURCE_BUCKET_NAME']
    kendra_rawdata_index_id = os.environ['KENDRA_INDEX_ID']
    sagemaker_pricing_database = os.environ['SAGEMAKER_PRICING_DATABASE']
    log_level = os.environ['LOG_LEVEL']

    kendra_client = boto3.client("kendra", region_name=region_name)
    s3_resource = boto3.resource("s3", region_name=region_name)
    bedrock_client = boto3.client("bedrock-runtime", region_name=region_name)

    @staticmethod
    def get_bedrock_llm(model_name="Claude2.1", max_tokens=256, cache=False):
        MODELID_MAPPING = {
            "Titan": "amazon.titan-tg1-large",
            "Claude2.1": "anthropic.claude-v2:1",
            "Claude2": "anthropic.claude-v2",
            "ClaudeInstant": "anthropic.claude-instant-v1",
        }

        MODEL_KWARGS_MAPPING = {
            "Titan": {
                "maxTokenCount": max_tokens,
                "temperature": 0,
                "topP": 1,
            },
            "Claude2.1": {
                "max_tokens_to_sample": max_tokens,
                "temperature": 0,
                "top_p": 1,
                "top_k": 50,
            },
            "Claude2": {
                "max_tokens_to_sample": max_tokens,
                "temperature": 0,
                "top_p": 1,
                "top_k": 50,
            },
            "ClaudeInstant": {
                "max_tokens_to_sample": max_tokens,
                "temperature": 0,
                "top_p": 1,
                "top_k": 50,
            },
        }

        model = model_name
        llm = Bedrock(
            client=Connections.bedrock_client,
            model_id=MODELID_MAPPING[model],
            model_kwargs=MODEL_KWARGS_MAPPING[model],
            cache=cache
            # model_kwargs=json.loads(body)
        )
        return llm
