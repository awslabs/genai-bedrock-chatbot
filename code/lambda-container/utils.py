import re


def parse_agent_output(output):
    """
    This is to parse the output the agent into a JSON format

    Input:
        output (str): agent call output
    Output"
        output (dic): reformatted output
    """

    # Define regex patterns to match 'text' and 'source' sections
    text_pattern = r'"text"\s*:\s*"([^"]*)"'
    source_pattern = r'"source"\s*:\s*"([^"]*)'

    # Use regex to search for and extract the 'text' and 'source' sections
    text_match = re.search(text_pattern, output)
    source_match = re.search(source_pattern, output)

    if text_match:
        text = text_match.group(1)
    else:
        text = ""

    if source_match:
        source = source_match.group(1)
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
    import re

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
