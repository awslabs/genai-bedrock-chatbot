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
    logging.info("events: %s", event)
    try:
        payload = json.loads(event["body"])
        logging.debug("Lambda Payload: %s", payload)

        query = payload["query"]
        session_id = payload["session_id"]

        output = get_response(query, session_id)
    except Exception as e:
        logging.exception("Error processing request")
        output = {"source": " ", "answer": f"Error processing your request: {e}"}

    return output
