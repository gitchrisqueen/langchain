from typing import Tuple, Dict

import langchain.globals
import streamlit as st
# from dotenv import load_dotenv

from langchain.agents import initialize_agent, Tool, tool, AgentExecutor
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationSummaryBufferMemory, ConversationBufferMemory
from langchain.schema import SystemMessage
from langchain.callbacks import StreamlitCallbackHandler
from langchain.tools.render import format_tool_to_openai_function, format_tool_to_openai_tool

from langchain.globals import set_debug, set_verbose, get_verbose
from langchain_core.tools import StructuredTool

from langchain_community.agent_toolkits.usemotion.toolkit import UseMotionToolkit
from langchain_community.utilities.usemotion import UseMotionAPIWrapper

from langchain import hub
from langchain.agents import (AgentExecutor )


set_debug(True)
set_verbose(True)

# from aiagents.utils import motion

# 1. Load environment variables
# load_dotenv()


llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")


class Config():
    """
    Contains the configuration of the LLM.
    """
    model = 'gpt-3.5-turbo-16k-0613'
    llm = ChatOpenAI(temperature=0, model=model)


# 2. Setup agent memory and system message.
def setup_memory() -> Tuple[Dict, ConversationBufferMemory]:
    """
    Sets up memory for the open ai functions agent.
    :return a tuple with the agent keyword pairs and the conversation memory.
    """

    system_message = SystemMessage(
        content="""
        You are Motion calendar management expert. Assist the user the best you can using the tools you have.
        
        Use the following format:
        
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of your tools functions.
        Action Input: the input to the action (try to resolve validation errors)
        Observation: the result of the action
        .. (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question
        
        Begin!
        
        Question: {input}
        Thought: {agent_scratchpad}
               """
    )

    chat_history = MessagesPlaceholder(variable_name="chat_history")
    # memory = ConversationBufferMemory(memory_key="memory", return_messages=True)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    agent_kwargs = {
        # "extra_prompt_messages": [chat_history],
        "system_message": system_message,
        "memory_prompts": [chat_history],
        "input_variables": ["input", "agent_scratchpad", "chat_history"],
        "verbose": get_verbose(),
    }

    return agent_kwargs, memory


# 3. Create langchain agent with the tools above
def setup_agent() -> AgentExecutor:
    """
    Sets up the tools for a function based chain.
    We have here the following tools:
    - list_workspaces
    - get_iso_date
    - get_tasks
    - retrieve_task
    - create_task
    - update_task
    """
    cfg = Config()
    # tools = [
    #    motion.ListWorkspacesTool(),
    #    motion.GetISODateTool(),
    #    motion.CreateTaskTool(),
    #    motion.RetieveTaskTool(),
    #    motion.GetTasksTool(),
    #    motion.UpdateTaskTool()

    # ]

    motion = UseMotionAPIWrapper()
    toolkit = UseMotionToolkit.from_motion_api_wrapper(motion)
    tools = toolkit.get_tools()

    # TODO:  Add additional tools here

    agent_kwargs, memory = setup_memory()

    agent = initialize_agent(
        tools,
        cfg.llm,
        # agent=AgentType.OPENAI_FUNCTIONS,
        # agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=get_verbose(),
        agent_kwargs=agent_kwargs,
        memory=memory,
        handle_parsing_errors=True,
        max_iterations=5,
        early_stopping_method="generate"
    )

    # Get the prompt to use - you can modify this!
    #prompt = hub.pull("hwchase17/structured-chat-agent")

    # Construct the JSON agent
    # agent2 = create_structured_chat_agent(cfg.llm, tools, prompt)

    # Create an agent executor by passing in the agent and tools
    # agent_executor = AgentExecutor(
    #    agent=agent, tools=tools, verbose=True, handle_parsing_errors=True,
    #    agent_kwargs=agent_kwargs,
    #    memory=memory,
    # )

    return agent


# Use streamlit to create a web app
def init_stream_lit_old():
    st.set_page_config(page_title="AI Motion Calendar Agent", page_icon=":bird:")

    st.header("AI Motion Calendar Agent :bird:")

    # query = st.text_input("Give me a task for your calendars.")

    # if query:
    #    st.write("Managing Calendar: ", query)

    #    result = agent({"input": query})

    #    st.info(result['output'])

    agent_executor: AgentExecutor = prepare_agent()

    if prompt := st.chat_input():
        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"):
            st_callback = StreamlitCallbackHandler(st.container())
            response = agent_executor.run(prompt, callbacks=[st_callback])
            st.write(response)


QUESTION_HISTORY: str = 'question_history'


def init_stream_lit():
    title = "AI Motion Calendar Agent"
    st.set_page_config(page_title=title, layout="wide")
    agent_executor: AgentExecutor = prepare_agent()

    st.header(title)
    if QUESTION_HISTORY not in st.session_state:
        st.session_state[QUESTION_HISTORY] = []
    intro_text()
    simple_chat_tab, historical_tab = st.tabs(["Simple Chat", "Session History"])
    if user_question := st.chat_input():
        st.chat_message("user").write(user_question)
        with simple_chat_tab:
            with st.chat_message("assistant"):
                try:
                    response = agent_executor.run(
                        #user_question,
                        input=user_question,
                        chat_history=st.session_state[QUESTION_HISTORY],
                        callbacks=[StreamlitCallbackHandler(st)]
                    )
                    st.write(f"{response}")
                    st.session_state[QUESTION_HISTORY].append((user_question, response))
                except Exception as e:
                    st.error(f"Error occurred: {e}")
    with historical_tab:
        for q in st.session_state[QUESTION_HISTORY]:
            question = q[0]
            if len(question) > 0:
                st.write(f"Q: {question}")
                st.write(f"A: {q[1]}")


def intro_text():
    with st.expander("Click to see application info:"):
        st.write(f"""Ask questions about:
- Adding task to calendar workspaces
    """)


@st.cache_resource()
def prepare_agent() -> AgentExecutor:
    return setup_agent()


if __name__ == "__main__":
    init_stream_lit()
