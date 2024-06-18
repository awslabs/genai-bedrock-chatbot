import json

from collections import OrderedDict

import logging
from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.schema import StrOutputParser, SystemMessage
from langchain_community.retrievers import AmazonKendraRetriever as KendraRetriever
from connections import Connections
from utils import get_by_session_id
from prompt_templates import RAG_SYS, RAG_TEMPLATE


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
    # instantiate retriever
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
    context = ""
    for i, doc in enumerate(docs):
        context += doc.metadata["excerpt"]

    prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=(RAG_SYS)),
                HumanMessagePromptTemplate.from_template(RAG_TEMPLATE),
            ]
        )
    llm = Connections.get_bedrock_llm(model_name="Claude3Sonnet", max_tokens=1024)
    rag_chain = {
            "context": itemgetter("context"),
        } | prompt | llm | StrOutputParser()

    rag_chain_with_memory = RunnableWithMessageHistory(
        rag_chain,
        get_by_session_id,
        input_messages_key="question",
        history_messages_key="history",
    )
    answer = rag_chain_with_memory.invoke(
        {"context": context,
         "question": query},
        config={"configurable": {"session_id": "1"}}
    )
    # Data to be written
    output = {"source": refs_str, "answer": answer}
    logging.debug(output)
    return output
