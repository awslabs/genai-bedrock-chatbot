import json
import logging
from index import get_response
from connections import Connections

logging.getLogger().setLevel(Connections.log_level)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)


def lambda_handler(event, context):
    """
    Lambda handler to answer user's question
    """
    logging.info(f"events: {event}")
    payload = json.loads(event["body"])
    # payload = json.loads(json.loads(event)['body']) # for local testing
    logging.info(f"Lambda Payload: {payload}")

    query = payload["query"]
    session_id = payload["session_id"]

    output = get_response(query, session_id)

    return output
