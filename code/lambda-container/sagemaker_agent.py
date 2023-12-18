import re
from typing import List, Union

from sagemaker_pricing import query_engine
from sagemaker_dg_rag import doc_retrieval
from prompt_templates import AGENT_TEMPLATE_WITH_HISTORY
from utils import parse_agent_output

from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.agents import Tool
from langchain.agents import AgentOutputParser, LLMSingleActionAgent
from langchain.schema import AgentAction, AgentFinish
from langchain.prompts import StringPromptTemplate
from langchain.agents import AgentExecutor
from langchain.chains import LLMChain


class CustomPromptTemplate(StringPromptTemplate):
    """
    Customize Prompts using StringPromptTemplate object
    """

    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join(
            [f"{tool.name}: {tool.description}" for tool in self.tools]
        )
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)


class CustomOutputParser(AgentOutputParser):
    """
    Parse Agent output
    """

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split(
                    "Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(
            tool=action,
            tool_input=action_input.strip(" ").strip('"'),
            log=llm_output,
        )


def doc_tool(reasoning_query):
    """
    Tool for RAG
    """
    output = doc_retrieval(reasoning_query)

    return output


def pricing_tool(reasoning_query):
    """
    Tool for querying SageMaker pricing data
    """
    response = query_engine.query(reasoning_query)
    output = response.response

    return output


def agent_call(llm, query):
    """
    Agent with access to document retrieval tool and PI real-time data retrieval tool, to solve the Use Case 3 milestone questions.

    Inputs:
        llm (object): a LLM object, initialized with Amazon Bedrock client
        query (str): question from the user.
    Output:
        output (dict): answer to the input question.
    """
    rag_tool = Tool(
        name="sagemaker developer guide",
        func=doc_tool,
        description="Useful for when you need to query the Amazon Kendra index for more information on SageMaker documentation. Input should be a question formated as a string.",
    )
    data_tool = Tool(
        name="sagemaker pricing data retrieval",
        func=pricing_tool,
        description="Useful for when you need to have access to pricing table data. Input should be a question.",
    )
    tools = [rag_tool, data_tool]

    prompt_with_history = CustomPromptTemplate(
        template=AGENT_TEMPLATE_WITH_HISTORY,
        tools=tools,
        # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
        # This includes the `intermediate_steps` variable because that is needed
        input_variables=["input", "intermediate_steps", "history"],
    )
    llm_chain = LLMChain(llm=llm, prompt=prompt_with_history)
    tool_names = [tool.name for tool in tools]

    def _handle_error(error) -> str:
        return str(error)[:50]

    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=CustomOutputParser(),
        stop=["\nObservation:"],  # Stopping Condition
        allowed_tools=tool_names,
        return_source_documents=True,
        return_intermediate_steps=True,
        handle_parsing_errors=_handle_error,
    )
    memory = ConversationBufferWindowMemory(k=10)
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=True, memory=memory
    )
    result = agent_executor.run(f"\n\nHuman:{query}\n\nAssistant:")
    result = parse_agent_output(result)
    # Data to be written
    output = {"source": result["source"], "answer": result["text"]}
    # output = {"answer": result}
    return output
