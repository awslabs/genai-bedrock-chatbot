import os
import boto3

from botocore.config import Config


class Connections:
    region_name = os.environ['AWS_REGION']
    lambda_function_name = os.environ['LAMBDA_FUNCTION_NAME']
    log_level = os.environ['LOG_LEVEL']

    lambda_client = boto3.client('lambda', region_name=region_name, config=Config(
        read_timeout=300, connect_timeout=300))
