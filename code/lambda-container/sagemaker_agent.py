import logging

from sagemaker_pricing import query_engine
from sagemaker_dg_rag import doc_retrieval
from utils import parse_agent_output

from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool


@tool
def sagemaker_developer_guide(query: str) -> str:
    """Useful for when you need to query the Amazon Kendra index for more information on SageMaker documentation. Input should be a question formatted as a string."""
    output = doc_retrieval(query)
    return str(output)


@tool
def sagemaker_pricing_data_retrieval(query: str) -> str:
    """Useful for when you need to have access to pricing table data. Input should be a question."""
    response = query_engine.query(query)
    return response.response


SYSTEM_PROMPT = """You are an expert in AWS SageMaker services and EC2 pricing.
You have access to tools for querying SageMaker documentation and pricing data.

Guidelines:
- If asked about pricing data such as instance price, compute optimized, memory, accelerated computing, storage, instance features, instance performance etc., use the sagemaker_pricing_data_retrieval tool.
- Use EC2 instances with GPUs to train deep learning models.
- Do not make up any answer.
- Format the final text answer in Markdown style, ADD '\\' ahead of each $.
- Include the source file from the sagemaker_developer_guide tool in the final answer.
- The final answer format should be in JSON format with the keys as "text" and "source".
- If the final answer comes only from the "sagemaker_pricing_data_retrieval" tool, set "source" as "[Amazon SageMaker Pricing](https://aws.amazon.com/sagemaker/pricing/)"
"""


def agent_call(llm, query):
    """
    Agent with access to document retrieval tool and pricing data retrieval tool.

    Inputs:
        llm (object): a LLM object, initialized with Amazon Bedrock client
        query (str): question from the user.
    Output:
        output (dict): answer to the input question.
    """
    tools = [sagemaker_developer_guide, sagemaker_pricing_data_retrieval]

    agent = create_react_agent(model=llm, tools=tools, prompt=SYSTEM_PROMPT)
    result = agent.invoke({"messages": [("user", query)]})

    output_text = result["messages"][-1].content
    logging.debug("Agent output: %s", output_text)
    parsed = parse_agent_output(output_text)
    logging.debug("Parsed agent output: %s", parsed)
    output = {"source": parsed["source"], "answer": parsed["text"]}
    return output
