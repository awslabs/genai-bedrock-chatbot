"""
Starting script of streamlit app.
"""
from datetime import datetime
import logging
import json
import streamlit as st
from streamlit_chat import message
from utils import (
    clear_input,
    show_empty_container,
    show_footer
)
from connections import Connections

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

lambda_client = Connections.lambda_client


def get_response(user_input, session_id):
    """
    Get response from genai Lambda
    """
    print(f"session id: {session_id}")
    payload = {"body": json.dumps(
        {"query": user_input, "session_id": session_id})}

    lambda_function_name = Connections.lambda_function_name

    response = lambda_client.invoke(
        FunctionName=lambda_function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )
    response_output = json.loads(response["Payload"].read().decode("utf-8"))
    print(f"response_output from genai lambda: {response_output}")

    return response_output


def header():
    """
    App Header setting
    """
    # --- Set up the page ---
    st.set_page_config(
        page_title="SageMaker (Pricing) Chatbot", page_icon=":rock:", layout="centered"
    )
    st.image(
        "https://pypi-camo.global.ssl.fastly.net/a16d902540297868fece35aa6b6704677f07ad90/68747470733a2f2f6769746875622e636f6d2f6177732f736167656d616b65722d707974686f6e2d73646b2f7261772f6d61737465722f6272616e64696e672f69636f6e2f736167656d616b65722d62616e6e65722e706e67",
        width=250,
    )
    st.header("SageMaker (Pricing) Demo")
    st.write("Ask me about SageMaker, and SageMaker Pricing on training/inference")
    st.write("-----")


def initialization():
    """
    Initialize sesstion_state variablesß
    """
    # --- Initialize session_state ---
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(datetime.now()).replace(" ", "_")
        st.session_state.questions = []
        st.session_state.answers = []

    if "temp" not in st.session_state:
        st.session_state.temp = ""

    # Initialize cache in session state
    if "cache" not in st.session_state:
        st.session_state.cache = {}


def show_message():
    """
    Show user question and answers
    """

    # --- Start the session when there is user input ---
    user_input = st.text_input("# **Question:** 👇", "", key="input")
    # Start a new conversation
    new_conversation = st.button(
        "New Conversation", key="clear", on_click=clear_input)
    if new_conversation:
        st.session_state.session_id = str(datetime.now()).replace(" ", "_")
        st.session_state.user_input = ""

    if user_input:
        session_id = st.session_state.session_id
        with st.spinner("Gathering info ..."):
            vertical_space = show_empty_container()
            vertical_space.empty()
            output = get_response(user_input, session_id)
            print(f"Output: {output}")
            result = output["answer"]
            st.write("-------")
            source_title = "**Source**:" + \
                output["source"] + "\n" + "**Answer**:\n"
            st.session_state.questions.append(user_input)
            st.session_state.answers.append(source_title + result)

    if st.session_state["answers"]:
        for i in range(len(st.session_state["answers"]) - 1, -1, -1):
            message(
                st.session_state["questions"][i],
                is_user=True,
                key=str(i) + "_user",
                logo="https://api.dicebear.com/7.x/notionists-neutral/svg?seed=Felix",
                allow_html=True,
            )
            message(
                st.session_state["answers"][i],
                key=str(i),
                logo="https://api.dicebear.com/6.x/icons/svg?seed=Chloe&backgroundColor=000000&radius=0",
                allow_html=True,
            )


def main():
    """
    Streamlit APP
    """
    # --- Section 1 ---
    header()
    # --- Section 2 ---
    initialization()
    # --- Section 3 ---
    show_message()
    # --- Foot Section ---
    show_footer()


if __name__ == "__main__":
    main()
