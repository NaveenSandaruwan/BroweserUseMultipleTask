import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
import os
import sys
import json
from dotenv import load_dotenv
from typing import Dict, List, Any
from typing import Literal
from langgraph.graph import StateGraph, END, START
import pprint

from langchain_core.messages import HumanMessage

from langchain_core.tools import tool


load_dotenv()

# Import your existing functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from browseruse.Agent.utils.jsonextract import extract_first_steps_json,extract_and_format_first_json
from browseruse.tools.browserUseClient import send_task
from browseruse.tools.dragTool import Toolbox
from browseruse.tools.filter import filter_json, find_used_blocks, get_list_of_used_blocks, get_category_coordinates, generate_detailed_blocks_summary
from browseruse.tools.execution import Executor
from browseruse.Agent.reactAgents import command_agent,explaining_agent,debugging_agent,general_coding_agent,format_agent,general_agent
from browseruse.Agent.utils.state import State
from browseruse.Agent.utils.tool import make_blocks

GEMINIAPI = os.getenv("GOOGLE_API_KEY")
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GEMINIAPI,
    temperature=0.3  # Lower temperature for more consistent responses
)

model2 = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GEMINIAPI,
    temperature=0.1  # Lower temperature for more consistent responses
)

executor = Executor()


def llm_router(state: State) -> Literal["code_explain", "code_debugging", "give_instructions","make_blocks"]:
    query = state["query"]
    response = model2.invoke(
        f"""
You are a router agent that decides which expert agent should handle the user's request based on its content.
Given the user's query below, choose the most appropriate agent to handle it:
User Query: "{query}"
  - code_explain -> Explain working space (user's code) of the user.
  - code_debugging -> Help user debug their Scratch programs.
  - give_instructions -> Provide step-by-step instructions for using Scratch and How to code using Scratch. If user ask to give instuctions to do certain task, choose this.
  - make_blocks -> Create Scratch blocks based on user input. If user want some help to create blocks, choose this. If user want to See how to do something, choose make_blocks.
  - make_blocks -> Specially key words like "Create blocks", "Make blocks", "Show me how to do this in blocks", "How to do this in blocks", "Help me create blocks", "Help me make blocks", "I want to see the blocks for this", "I want to see how to do this in blocks", "Show me the blocks for this", "Show me how to do this in blocks", "Can you create the blocks for this?", "Can you make the blocks for this?", "Can you show me the blocks for this?", "Can you show me how to do this in blocks?", "I need help creating blocks", "I need help making blocks", "I need help with the blocks for this", "I need help with how to do this in blocks", "Please create the blocks for this", "Please make the blocks for this", "Please show me the blocks for this", "Please show me how to do this in blocks". If user say any of these or similar, choose make_blocks.
  - general_agent -> For all other queries that do not fit the above categories if it is a just not code related, provide a general response. If use say "Hi", "Hello", "Thank you", "Thanks", "What is your name?", "Who are you?" or any other general question like this, choose this.

  specially identify if the user is asking for instructions on how to do something in Scratch, or if they want you to create blocks for them. In these cases, you must choose "give_instructions" or "make_blocks" respectively.
  always choose one of these options: code_explain, code_debugging, give_instructions, make_blocks, default. According to the definitions given above.
  .
"""
    )
    choice = response.content.strip().lower()
    print(f"Router choice: {choice}")
    if choice not in ["code_explain", "code_debugging", "give_instructions", "make_blocks","general_agent"]:
        choice = "code_explain"
    return choice

def handle_execution_error(state: State) -> Literal["make_blocks","fromat_response"]:
    execution_result = state['result']['execute_blocks']
    
    if execution_result== "false":
        return "make_blocks"
    else:
        return "format_response"
    
def code_explain_node(state: State) -> State:
    send_task("refresh")
    time.sleep(2) 
    web_application_coding_summary = generate_detailed_blocks_summary(include_all_blocks=True)
    working_space = get_list_of_used_blocks()
    # print("Working space:", working_space)

    # Compose a message that includes the query, coding summary, and working space
    message = (
        f"User Query: {state['query']}\n\n"
        f"Scratch Block Summary and functionalities of blocks in each category:\n{web_application_coding_summary}\n\n"
        f"Current Workspace ( you can see what user have done):\n{working_space}"
    )

    result = explaining_agent.invoke({"messages": [HumanMessage(content=message)]})
    return {"result": {"explanation": result["messages"][-1].content}}

def code_debugging_node(state: State) -> State:

    send_task("refresh")
    print("Refreshing workspace for debugging...")
    time.sleep(2)  # wait for 2 seconds to ensure the workspace is updated
    web_application_coding_summary = generate_detailed_blocks_summary(include_all_blocks=True)
    working_space = get_list_of_used_blocks()

    # Compose a message that includes the query, coding summary, and working space
    message = (
        f"User Query: {state['query']}\n\n"
        f"Scratch Block Summary and functionalities of blocks in each category:\n{web_application_coding_summary}\n\n"
        f"Current Workspace ( you can see what user have done):\n{working_space}"
    )

    result = debugging_agent.invoke({"messages": [HumanMessage(content=message)]})
    return {"result": {"debugging_advice": result["messages"][-1].content}}

def give_instructions_node(state: State) -> State:
    web_application_coding_summary = generate_detailed_blocks_summary(include_all_blocks=True)
    # print("Web application coding summary:", web_application_coding_summary)
    message = (
        f"User Query: {state['query']}\n\n"
        f"Scratch Block Summary and functionalities of blocks in each category:\n{web_application_coding_summary}\n\n"
        
        )
    result = general_coding_agent.invoke({"messages": [HumanMessage(content=message)]})
    return {"result": {"instructions": result["messages"][-1].content}}

def make_blocks_node(state: State) -> State:
    send_task("refresh")
    time.sleep(1)  # wait for 2 seconds to ensure the workspace is updated
    result = command_agent.invoke({"messages": [state['result']['instructions']]})
    return {"result": {"make_blocks": result["messages"][-1].content}}

def execute_blocks_node(state: State) -> State:
    # take state['result']['make_blocks'] and extract json object from it
    json_object = extract_and_format_first_json(state['result']['make_blocks'])
    # print("Extracted JSON:", json_object)
    try:
        result = make_blocks(json_object)
        # time.sleep(10)  # wait for 2 seconds to ensure the workspace is updated
        result = "true"
    except Exception as e:
        result = f"false"
        # print(f"Error occurred: {e}")
    # print(json_object)
    finally:
    # result = command_executor.invoke({"messages": [state['result']['make_blocks']]})
        return {"result": {"execute_blocks": result}}

def general_agent_node(state: State) -> State:
    result = general_agent.invoke({"messages": [HumanMessage(content=state["query"])]})
    return {"result": {"general_response": result["messages"][-1].content}}


def format_response(state: State) -> State:
    # Extract the actual text content from the result dictionary
    if "result" in state:
        # Get the first value from the inner dictionary
        result_content = next(iter(state["result"].values()))
        
        # Pass the string content to HumanMessage
        result = format_agent.invoke({"messages": [HumanMessage(content=result_content)]})
        return {"result": {"formatted_response": result["messages"][-1].content}}
    return state
