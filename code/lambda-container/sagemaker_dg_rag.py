import json
from langchain_community.retrievers import AmazonKendraRetriever as KendraRetriever
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from connections import Connections
from collections import OrderedDict
from prompt_templates import CONVERSATION_CHAIN_TEMPLATE
import logging

s3_resource = Connections.s3_resource


def source_link(input_source):
    """
    Retrieve source url of relevant documents
    """
    string = input_source.partition(
        f"s3.{Connections.region_name}.amazonaws.com/")[2]
    bucket = string.partition("/")[0]
    obj = string.partition("/")[2]
    file = s3_resource.Object(bucket, obj)
    body = file.get()["Body"].read()
    res = json.loads(body)
    source_link = res["Url"]
    return source_link


def doc_retrieval(query, llm_model="ClaudeInstant", K=5):
    """
    Answer user's query about Amazon SageMaker
    """
    # custom prompt template for ConversationChain(), the defualt template is too simple, and not customerized for Claude models.
    memory = ConversationBufferMemory(ai_prefix="Assistant")
    llm = Connections.get_bedrock_llm(model_name=llm_model, max_tokens=1024)
    custom_prompt = PromptTemplate(
        input_variables=["history", "input"], template=CONVERSATION_CHAIN_TEMPLATE
    )
    conversation = ConversationChain(
        llm=llm, prompt=custom_prompt, verbose=False, memory=memory
    )
    retriever = KendraRetriever(
        kclient=Connections.kendra_client,
        top_k=K,
        index_id=Connections.kendra_rawdata_index_id,
    )
    docs = retriever._get_relevant_documents(query, run_manager=None)

    # return the top 5 sources
    source_list = []
    for i, doc in enumerate(docs):
        title = doc.metadata["title"]
        # remove '\n' in the title
        title_without_newlines = title.replace("\n", "")
        cleaned_title = " ".join(title_without_newlines.split())
        s3_link = doc.metadata["source"]
        web_link = source_link(s3_link)
        source_dict = (cleaned_title, web_link)
        source_list.append(source_dict)

    # get the unique sources
    unique_sources = list(OrderedDict.fromkeys(source_list))
    # put the sources information into a string
    refs_str = ""
    for i, x in enumerate(list(unique_sources)):
        refs_str += f"{i + 1}. " + "[" + str(x[0]) + "](%s)" % (x[1]) + "\n\n"

    # put the retrieved information and previous questions and answers in memory
    for i, doc in enumerate(docs):
        memory.save_context(
            {"input": "context: " + doc.metadata["excerpt"]},
            {"output": ""},
        )

    res = conversation.predict(input=f"\n\nHuman:{query}\n\nAssistant:")
    # remove the hunman and AI conversation is there is any in the answer
    res_filter = res.split("Human:", 1)
    answer = res_filter[0]
    if answer[0] == " ":
        answer = answer[1:]

    # Data to be written
    output = {"source": refs_str, "answer": answer}
    logging.debug(output)
    return output
