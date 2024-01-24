"""
This script is to leverage few shots prompting to understand user's question intent.
"""

import logging
from langchain.prompts import PromptTemplate
from langchain.prompts import FewShotPromptTemplate


def get_question_intent_general(llm, query):
    """
    This function is to classify the query intent with a few shot prompts.
    Three categories: "Use Case 1", "Use Case 2", "Use Case 3  are the choices.

    Input:
        llm: LLM object
        query: user's question
    Output:
        query intent as a str.
    """
    logging.info("Getting query intent")
    # create our examples
    examples = [
        {
            "query": "What is SageMaker?",
            "answer": "Use Case 1",
        },
        {
            "query": "Can SageMaker provide monitoring service?",
            "answer": "Use Case 1",
        },
        {
            "query": "Tell me about sagemaker deployment",
            "answer": "Use Case 1",
        },
        {
            "query": "What is the cheapeast GPU instance?",
            "answer": "Use Case 1",
        },
        {
            "query": "Which instance should I use to train Stable Diffusion model and how much will the training cost?",
            "answer": "Use Case 1",
        },
        {
            "query": "which instance should I use to train Stable Diffusion model?",
            "answer": "Use Case 1",
        },
        {
            "query": "Which instance should I use to train a deep learning model within a budget of $100?",
            "answer": "Use Case 1",
        },
        {
            "query": "I want to finetune a Stable Diffusion model. Please recommend a GPU instance and estimate the time and cost for training.",
            "answer": "Use Case 1",
        },
        {
            "query": "How much is ml.p3.xlarge per hour for training?",
            "answer": "Use Case 2",
        },
        {
            "query": "which instance should I use to train a model like chatgpt?",
            "answer": "Use Case 2",
        },
        {
            "query": "How much does it cost to use an P3 instance for 10 hours?",
            "answer": "Use Case 2",
        },
        {
            "query": "What is ec2 instance c7g.8xlarge?",
            "answer": "Use Case 2",
        },
        {
            "query": "Is c7g.8xlarge better than p3.xlarge in deep learning training?",
            "answer": "Use Case 3",
        },
        {
            "query": "Which instance should I use to fine-tune Claude 1 model and how much does it cost?",
            "answer": "Use Case 3",
        },
        {
            "query": "How much does it cost to train Stable Diffusion model?",
            "answer": "Use Case 3",
        },
        {
            "query": "Why p3 instance is bettern than c5 instance in deep learning and what are the cost differences in training?",
            "answer": "Use Case 3",
        },
    ]
    # create a example template
    example_template = """
    \n\nHuman: {query}
    \n\nAssistant: {answer}
    """

    # create a prompt example from above template
    example_prompt = PromptTemplate(
        input_variables=["query", "answer"], template=example_template
    )

    # now break our previous prompt into a prefix and suffix
    # the prefix is our instructions
    # """

    prefix = """You are an expert of classifying intents of questions related to Amazon SageMaker. Use the instructions given below to determine question intent.
    Only answer in one of the following responses: "Use Case 1", "Use Case 2" and "Use Case 3"
    Do not answer outside of the three categories listed above.
        - "Use Case 1" questions are usually about simple guidance request. Choose "Use Case 1" if user query asks for a descriptive or qualitative answer.
        - "Use Case 2" questions are data related questions, such as pricing, or memory related.
        - "Use Case 3" questions are the combination of quantitative and guidance request and also about the reasons of some problem that needs in-context information and quantitative data.

    Please response with one of the three categories:
        "Use Case 1",
        "Use Case 2",
        "Use Case 3",


    Try your best to determine the question intent and DO NOT provide answer out of the four categories listed above. Here are some examples:
    """
    # and the suffix our user input and output indicator
    suffix = """
    \n\nHuman: {query}
    \n\nAssistant: """

    # now create the few shot prompt template
    few_shot_prompt_template = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix=prefix,
        suffix=suffix,
        input_variables=["query"],
        example_separator="\n\n",
    )
    res = llm(few_shot_prompt_template.format(query=query))

    res_filter = res.split("User:", 1)
    answer = res_filter[0]
    logging.debug("".join(answer.replace("\n", "").split(" ")))
    return "".join(answer.replace("\n", "").split(" "))
