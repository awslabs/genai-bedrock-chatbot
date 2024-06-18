import os
import boto3
from langchain_community.chat_models import BedrockChat
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
    def get_bedrock_llm(model_name="Claude2.1", max_tokens=256, cache=False, mode='chat'):
        MODELID_MAPPING = {
            "Claude2.1": "anthropic.claude-v2:1",
            "Claude2": "anthropic.claude-v2",
            "ClaudeInstant": "anthropic.claude-instant-v1",
            "Claude3Sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
            "Claude3Haiku": "anthropic.claude-3-haiku-20240307-v1:0",
        }

        MODEL_KWARGS_MAPPING = {
            "Claude2.1": {
                "temperature": 0,
                "top_p": 1,
                "top_k": 50,
                "stop_sequences": ["\n\nHuman"]
            },
            "Claude2": {
                "temperature": 0,
                "top_p": 1,
                "top_k": 50,
                "stop_sequences": ["\n\nHuman"]
            },
            "ClaudeInstant": {
                "temperature": 0,
                "top_p": 1,
                "top_k": 50,
            },
            "Claude3Sonnet": {
                "max_tokens": max_tokens,
                "temperature": 0,
                "top_p": 1,
                "top_k": 50,
                "stop_sequences": ["\n\nHuman"],
            },
            "Claude3Haiku": {
                "max_tokens": max_tokens,
                "temperature": 0,
                "top_p": 1,
                "top_k": 50,
                "stop_sequences": ["\n\nHuman"],
            },
        }

        model = model_name
        llm_class = BedrockChat if mode == 'chat' else Bedrock

        model_kwargs = MODEL_KWARGS_MAPPING[model]
        if mode == 'chat':
            model_kwargs['max_tokens'] = max_tokens
        else:
            model_kwargs['max_tokens_to_sample'] = max_tokens

        llm = llm_class(
            client=Connections.bedrock_client,
            model_id=MODELID_MAPPING[model],
            model_kwargs=model_kwargs,
            cache=cache
        )
        return llm
