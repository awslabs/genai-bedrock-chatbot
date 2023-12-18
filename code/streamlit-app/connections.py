import os
import boto3

from langchain.llms import Bedrock
from botocore.config import Config


class Connections:
    region_name = os.environ['AWS_REGION']
    lambda_function_name = os.environ['LAMBDA_FUNCTION_NAME']
    log_level = os.environ['LOG_LEVEL']

    lambda_client = boto3.client('lambda', region_name=region_name, config=Config(
        read_timeout=300, connect_timeout=300))

    @staticmethod
    def get_bedrock_llm(model_name="Claude1", max_tokens=256, cache=False):
        MODELID_MAPPING = {
            "Titan": "amazon.titan-tg1-large",
            "Claude1": "anthropic.claude-v1",
            "Jurassic": "ai21.j2-ultra-v1",
            "Claude2": "anthropic.claude-v2",
            "ClaudeInstant": "anthropic.claude-instant-v1"
        }

        MODEL_KWARGS_MAPPING = {
            "Titan": {
                "maxTokenCount": max_tokens,
                "temperature": 0,
                "topP": 1,
            },
            "Claude1": {
                "max_tokens_to_sample": max_tokens,
                "temperature": 0,
                "top_p": 1,
                "top_k": 50,
            },
            "Jurassic": {
                "maxTokens": max_tokens,
                "temperature": 0,
                "topP": 1,
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
