import re
from typing import List
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.pydantic_v1 import BaseModel, Field


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []


def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    """
    Get a chat message history by session id.

    Args:
        session_id: The session id to get the history for.

    Returns:
        The chat message history for the session id.
    """
    store = {}
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]


def parse_agent_output(output):
    """
    This is to parse the output the agent into a JSON format

    Input:
        output (str): agent call output
    Output"
        output (dic): reformatted output
    """

    # Define regex patterns to match 'text' and 'source' sections
    text_pattern = r"['\"]text['\"]\s*:\s*['\"]([^']*)['\"]"
    source_pattern = r"['\"]source['\"]\s*:\s*['\"]([^']*)['\"]"

    # Use regex to search for and extract the 'text' and 'source' sections
    text_match = re.search(text_pattern, output)
    source_match = re.search(source_pattern, output)

    if text_match:
        text = text_match.group(1).replace("\\'", "'")  # Handle escaped single quotes
    else:
        text = ""

    if source_match:
        source = source_match.group(1).replace(
            "\\'", "'"
        )  # Handle escaped single quotes
        source_title, source_link = reformat_source(source)
        source = f"[{source_title}]({source_link})"
    else:
        source = ""

    output = {"text": text, "source": source}
    return output


def reformat_source(source):
    """
    This function is to reformat source str

    Input:
        source (str): source file from agent output
    Outpit:
        source_title, source_link (tuple): source file title, and source link
    """
    # Define the regular expression pattern to match text within square brackets and parentheses
    pattern = r"\[(.*?)\]\(([^)]+)\)"

    # Search for the pattern in the input string
    matches = re.findall(pattern, source)

    if len(matches) > 0:
        # Extract the text within square brackets and parentheses
        source_title = ""
        source_link = ""
        for match in matches:
            text_in_square_brackets = match[0]
            text_in_parentheses = match[1]
            source_title = text_in_square_brackets
            source_link = text_in_parentheses
    else:
        source_title = source_link = source

    return source_title, source_link
