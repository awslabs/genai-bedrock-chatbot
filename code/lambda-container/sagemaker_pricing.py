from sqlalchemy import create_engine
from llama_index.objects import ObjectIndex, SQLTableNodeMapping, SQLTableSchema
from llama_index.indices.struct_store import SQLTableRetrieverQueryEngine
from llama_index import VectorStoreIndex
from llama_index import SQLDatabase
from llama_index import ServiceContext

# from utils import table_details, Connections, create_sql_engine
from langchain_community.embeddings import BedrockEmbeddings
from llama_index.prompts import Prompt
from connections import Connections
from prompt_templates import SQL_TEMPLATE_STR, RESPONSE_TEMPLATE_STR
import logging


table_details = {
    "real_time_inference_price": "real time inference instance price data, includes instance name, price, memory.Use this as default table if non specified",
    "training_price": "training instance price data, includes instance name, price, memory.",
    "asynchronous_inference_price": "asynchronous inference instance price data, includes instance name, price, memory",
    "inference_accelerator_price": "inference accelerator instance price data, includes instance name, price, memory",
}


SQL_PROMPT = Prompt(SQL_TEMPLATE_STR)
RESPONSE_PROMPT = Prompt(RESPONSE_TEMPLATE_STR)


def create_sql_engine():
    """
    Connect to Amazon Athena
    """
    s3_staging_dir = Connections.s3_pricing_bucket_name
    region = Connections.region_name
    database = Connections.sagemaker_pricing_database
    # Construct the connection string
    conn_url = f"awsathena+rest://athena.{region}.amazonaws.com/{database}?s3_staging_dir=s3://{s3_staging_dir}"
    # Create an SQLAlchemy engine
    engine = create_engine(conn_url)

    return engine


def display_prompt_dict(prompts_dict):
    for k, p in prompts_dict.items():
        logging.debug(p.get_template())


def create_query_engine(
    model_name="Claude2.1", SQL_PROMPT=SQL_PROMPT, RESPONSE_PROMPT=RESPONSE_PROMPT
):
    # create sql database object
    engine = create_sql_engine()
    sql_database = SQLDatabase(engine, sample_rows_in_table_info=2)

    # initialize llm
    llm = Connections.get_bedrock_llm(
        model_name=model_name, max_tokens=1024, cache=False
    )
    embeddings = BedrockEmbeddings(
        client=Connections.bedrock_client, model_id="amazon.titan-embed-text-v1"
    )
    # initialize service context
    service_context = ServiceContext.from_defaults(
        llm=llm, embed_model=embeddings)

    table_node_mapping = SQLTableNodeMapping(sql_database)
    table_schema_objs = []
    tables = list(sql_database._all_tables)
    for table in tables:
        table_schema_objs.append(
            (SQLTableSchema(table_name=table,
             context_str=table_details[table]))
        )

    obj_index = ObjectIndex.from_objects(
        table_schema_objs,
        table_node_mapping,
        VectorStoreIndex,
        service_context=service_context,
    )

    query_engine = SQLTableRetrieverQueryEngine(
        sql_database,
        obj_index.as_retriever(similarity_top_k=5),
        service_context=service_context,
        text_to_sql_prompt=SQL_PROMPT,
        response_synthesis_prompt=RESPONSE_PROMPT,
    )
    prompts_dict = query_engine.get_prompts()
    logging.debug("prompts_dict", prompts_dict)
    return query_engine, obj_index


query_engine, obj_index = create_query_engine()
