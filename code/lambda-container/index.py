from sagemaker_pricing import query_engine
from app_question_intent import get_question_intent_general
from sagemaker_dg_rag import doc_retrieval
from sagemaker_agent import agent_call
from connections import Connections
import logging


def get_response(user_input, session_id):
    """
    Get response RAG or Query
    """
    llm_qintent = Connections.get_bedrock_llm(
        model_name="ClaudeInstant", max_tokens=64, cache=False
    )

    llm_agent = Connections.get_bedrock_llm(
        model_name="Claude2.1", max_tokens=1024, cache=False
    )

    qintent = get_question_intent_general(llm=llm_qintent, query=user_input)
    logging.debug(f"Question {user_input}")
    logging.debug(f"Intent: {qintent}")
    if qintent == "UseCase2":
        response = query_engine.query(user_input)
        logging.debug(response.response)
        logging.debug("")
        logging.debug(response.metadata["sql_query"])
        output = {
            "source": response.metadata["sql_query"], "answer": response.response}
    elif qintent == "UseCase1":
        output = doc_retrieval(user_input)
    elif qintent == "UseCase3":
        output = agent_call(llm=llm_agent, query=user_input)
    else:
        output = {
            "source": ' ', "answer": "This is a malicious query. Please ask a proper question."}

    return output
