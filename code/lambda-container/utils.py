import json
import re
from typing import List
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

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


def _content_to_text(content):
    """
    Flatten an LLM message's content into plain text.

    Bedrock models that emit extended thinking return a list of content blocks
    (for example [{"type": "thinking", ...}, {"type": "text", "text": ...}])
    instead of a plain string, so text blocks are concatenated and non-text
    blocks are discarded.

    Input:
        content: message content as a str, a list of blocks, or None
    Output:
        content as a str
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(part for part in parts if part)
    if content is None:
        return ""
    return str(content)


def _repair_json_escapes(candidate):
    """
    Escape backslashes that do not start a valid JSON escape sequence.

    The agent prompt asks for a '\\' in front of every '$', which produces
    invalid JSON such as '\\$3.825'. Doubling those backslashes makes the
    payload parseable while preserving the intended Markdown escaping.

    Input:
        candidate (str): candidate JSON text
    Output:
        repaired JSON text as a str
    """
    return re.sub(r'\\(?!["\\/bfnrtu])', r"\\\\", candidate)


def _extract_json_object(text):
    """
    Best-effort extraction of a JSON object from a model response.

    Handles both a bare JSON object and one wrapped in a fenced code block, and
    retries with repaired escape sequences before giving up.

    Input:
        text (str): model response
    Output:
        dict if a JSON object was parsed, otherwise None
    """
    candidate = text.strip()

    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", candidate, re.DOTALL)
    if fenced:
        candidate = fenced.group(1)
    else:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start == -1 or end <= start:
            return None
        candidate = candidate[start : end + 1]

    for attempt in (candidate, _repair_json_escapes(candidate)):
        try:
            parsed = json.loads(attempt)
        except (ValueError, TypeError):
            continue
        if isinstance(parsed, dict):
            return parsed

    return None


def _first_match(patterns, text):
    """
    Return the first capture group matched by any of the given patterns.

    Input:
        patterns (tuple): regex patterns to try in order
        text (str): text to search
    Output:
        captured value as a str, or "" when nothing matched
    """
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # Handle escaped single quotes
            return match.group(1).replace("\\'", "'")
    return ""


def parse_agent_output(output):
    """
    This is to parse the output the agent into a JSON format

    The agent is prompted to answer with JSON containing "text" and "source",
    but compliance is not guaranteed: the response may arrive as a list of
    content blocks, as JSON inside a fenced code block, or as plain Markdown.
    Each case degrades gracefully so a usable answer is always returned rather
    than an empty one.

    Input:
        output: agent call output (str, or list of content blocks)
    Output"
        output (dic): reformatted output
    """
    text_str = _content_to_text(output)

    if not text_str.strip():
        return {"text": "", "source": ""}

    payload = _extract_json_object(text_str)
    if payload is not None:
        text = payload.get("text") or ""
        source = payload.get("source") or ""
    else:
        # Fall back to regex for near-JSON output, matching double-quoted
        # (JSON style) and single-quoted (Python repr style) values. Each
        # pattern stops at its own closing quote so a value cannot swallow the
        # following key.
        text_patterns = (
            r'"text"\s*:\s*"((?:[^"\\]|\\.)*)"',
            r"'text'\s*:\s*'((?:[^'\\]|\\.)*)'",
        )
        source_patterns = (
            r'"source"\s*:\s*"((?:[^"\\]|\\.)*)"',
            r"'source'\s*:\s*'((?:[^'\\]|\\.)*)'",
        )

        text = _first_match(text_patterns, text_str)
        source = _first_match(source_patterns, text_str)

        if not text:
            # The model answered in prose instead of JSON. Surface the answer
            # as-is rather than returning an empty response.
            text = text_str.strip()

    if source:
        source_title, source_link = reformat_source(source)
        source = f"[{source_title}]({source_link})"

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
