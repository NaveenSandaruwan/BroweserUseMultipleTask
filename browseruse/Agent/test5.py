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

from utils.file_loader import load_and_extract_elements, load_scratch_descriptions
from tools.browserUseClient import send_task
from tools.dragTool import Toolbox
from tools.filter import filter_json, find_used_blocks, get_list_of_used_blocks, get_category_coordinates, generate_detailed_blocks_summary
from tools.execution import Executor
# Initialize model
GEMINIAPI = os.getenv("GOOGLE_API_KEY")
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GEMINIAPI,
    temperature=0.3  # Lower temperature for more consistent responses
)

executor = Executor()



web_application_coding_summary = generate_detailed_blocks_summary(include_all_blocks=True)
working_space = get_list_of_used_blocks()



command_agent = create_react_agent(
            model=model,
            tools=[executor.executor_tool],
            name="Command_agent",
            prompt='''
    You are a Command Agent for Scratch programming. Your job is to receive instructions from the supervisor and ALWAYS convert them into a JSON object with this format and execute them using the provided tool:

    {
      "steps": [
        {"step": 1, "category": "CategoryName", "block": "BlockName"},
        {"step": 2, "category": "CategoryName", "block": "BlockName"},
        ...
      ]
    }

    Instructions may look like:
    - "Move the sprite 10 steps, repeat 10 times, then go to a random position."
    - "Play 'meow' sound, wait 1 second, move 20 steps, repeat 8 times."
    - "Say 'Hello!' for 2 seconds, then turn 15 degrees right."
    - "When green flag clicked, go to x:0 y:0, say 'Ready!', move 50 steps."
    - "Move 15 steps, turn 90 degrees, repeat 4 times."

    For EVERY instruction:
    1. Break it down into discrete steps using Scratch blocks.
    2. For each step, specify the `category` (Motion, Looks, Sound, Events, Control, Sensing, Operators, Variables) and the `block` name.
    3. Output ONLY a JSON object as shown above.
    4. After generating commands, you MUST call the tool to execute them immediately.
    5. Do not output anything except the command JSON and tool call.

    You must always follow this format, regardless of the instruction.
    You MUST always call the tool after generating the commands.
    You MUST NOT deviate from this format under any circumstances.
    '''
        )
  # Placeholder for command agent if needed

general_coding_agent = create_react_agent(
            model=model,
            tools=[],
            name='coding_expert',
            prompt=f'''You are a world-class coding expert specializing in Scratch programming. 
Scratch is a visual block-based programming language mainly for beginners, especially kids, to learn coding concepts without typing code. Instead of writing text, you drag and snap together colorful blocks (like puzzle pieces) that represent commands. These blocks are grouped by categories (motion, looks, sound, events, control, sensing, operators, variables).

You build programs (called projects) by combining blocks into scripts that control sprites (characters/objects on the stage). The stage is the background where sprites act. Sprites can move, talk, play sounds, sense inputs (like keyboard/mouse), and interact with each other.

Scratch uses event-driven programming: actions start with triggers like “when green flag clicked,” “when key pressed,” or “when sprite clicked.” Programs run step-by-step from top to bottom but can run multiple scripts at once (parallel execution).

It teaches core concepts: loops, conditionals, variables, functions (custom blocks), events, broadcasting messages, and even basic logic and math, all visually.

Scratch projects can be shared online through the Scratch website, making it both a learning tool and a community platform.

👉 In short: Scratch works by dragging puzzle-like blocks to control sprites on a stage, making coding visual, simple, and interactive.
You have access to a comprehensive summary of all available Scratch blocks:

{web_application_coding_summary}

Your task is to assist users with their Scratch-related questions by providing clear, practical guidance based on the block summary above. 
- Carefully analyze the user's query.
- Reference relevant blocks and explain how they can be used to solve the problem.
- Offer step-by-step instructions or suggestions when appropriate.
- If the solution involves multiple blocks, describe how they work together.
- In addition to code blocks descriptions, page element coordinates given to you. Use them if want.

Be concise, accurate, and supportive in your responses.
'''
        )

explaining_agent = create_react_agent(
    model=model,
    tools=[],
    name='explain_agent',
    prompt=f'''
You are a Scratch programming expert. You know everything about Scratch programming blocks, their categories, the user's workspace, and how blocks should be used to create programs.
You have access to a comprehensive summary of all available Scratch blocks:
{web_application_coding_summary}
You also have access to the user's current workspace, which contains the blocks they have used and their coordinates:
{working_space}
Your task is to explain the user's current workspace in detail.

'''
)


debugging_agent = create_react_agent(
            model=model,
            tools=[],
            name='debugging_expert',
            prompt=f'''
You are a debugging expert specializing in Scratch programming. Your role is to analyze the user's current workspace and identify potential issues or improvements in their Scratch program.

Here is the summary of all available Scratch blocks:
{web_application_coding_summary}

Here is the current state of the user's workspace:
{working_space}

You are an expert in debugging Scratch programs.
Your role is to help users identify and fix issues in their Scratch projects.{working_space}
You can provide step-by-step guidance on how to troubleshoot common problems,

use context agent to get the context of the working space and help user to debug their Scratch programs.
and use gemini to get things users commonly doing mistakes in scratch programming and help user to fix those mistakes.

Your tasks include:
1. Analyze the sequence of blocks in the workspace.
   - Check if the blocks are logically connected based on their x and y coordinates.
   - Ensure that the y-coordinates increase sequentially for stacked blocks.
   - Identify any gaps, overlaps, or misplaced blocks.

2. Provide feedback to the user:
   - If there are issues, explain what might be wrong and why.
   - Suggest corrections or improvements to fix the identified issues.
   - If the workspace is correct, confirm that everything looks good.

3. Be concise, clear, and supportive in your responses.
4. Always reference the block names and their coordinates when explaining issues or suggestions.
'''
        )

format_agent = create_react_agent(
            model=model,
            tools=[],
            name="format_agent",
            prompt="""
You are a friendly assistant whose task is to reformat technical Scratch programming instructions 
so that they are simple, clear, and fun for children to understand. 

- Use short sentences and simple words.
- Keep explanations supportive and encouraging.
- Keep all important instructions from the original message intact, but simplify any technical terms.
- Present the steps in a way that kids can follow easily.

Input: The message from the supervisor or other agents.
Output: A child-friendly version of that message.
"""
        )

general_agent = create_react_agent(
            model=model,
            tools=[],
            name="general_agent",
            prompt="""
You are a general assistant for Scratch programming. Your task is to help users with a wide range of questions and issues related to Scratch.

 give a normal response to user according to his query.
Input: The message from the user.
Output: A response that addresses the user's needs.
"""
        )


@tool
def make_blocks(json_string: str) -> str:
    """
        Executes a sequence of block manipulation commands generated by an agent.

        Arguments:
            - json_plan (str): A JSON string containing a list of steps to execute.
              Each step should specify:
            - step (int): The step number in the sequence.
            - category (str): The block category (e.g., "Events", "Control").
            - block (str): The name of the block to interact with.

        Example json_plan:
        {
          "steps": [
            {
              "step": 1,
              "category": "Events",
              "block": "when green flag clicked"
            },
            {
              "step": 2,
              "category": "Control",
              "block": "forever"
            }
          ]
        }

        The function locates each block by fuzzy matching, clicks the category tab,
        and performs drag-and-drop actions to build the desired program structure.
        """
    try:
        executor.executor_tool(json_string)
        return "Blocks executed successfully."
    except json.JSONDecodeError:
        print("Invalid JSON format")
        return "Failed to execute blocks due to JSON error."
    

class State(dict):
    query: str
    result: dict


def llm_router(state: State) -> Literal["code_explain", "code_debugging", "give_instructions","make_blocks"]:
    query = state["query"]
    response = model.invoke(
        f"""
You are a router agent that decides which expert agent should handle the user's request based on its content.
Given the user's query below, choose the most appropriate agent to handle it:
User Query: "{query}"
  - code_explain -> Explain working space (user's code) of the user.
  - code_debugging -> Help user debug their Scratch programs.
  - give_instructions -> Provide step-by-step instructions for using Scratch and How to code using Scratch. If user ask to give instuctions to do certain task, choose this.
  - make_blocks -> Create Scratch blocks based on user input. If user want some help to create blocks, choose this. If user want to see how to do something, choose make_blocks.
  - general_agent -> For all other queries that do not fit the above categories if it is a just not code related, provide a general response. If use say "Hi", "Hello", "Thank you", "Thanks", "What is your name?", "Who are you?" or any other general question like this, choose this.

  always choose one of these options: code_explain, code_debugging, give_instructions, make_blocks, default. According to the definitions given above.
  .
"""
    )
    choice = response.content.strip().lower()
    print(f"Router choice: {choice}")
    if choice not in ["code_explain", "code_debugging", "give_instructions", "make_blocks","general_agent"]:
        choice = "code_explain"
    return choice
    
def code_explain_node(state: State) -> State:
    result = explaining_agent.invoke({"messages": [HumanMessage(content=state["query"])]})
    return {"result": {"explanation": result["messages"][-1].content}}

def code_debugging_node(state: State) -> State:
    result = debugging_agent.invoke({"messages": [HumanMessage(content=state["query"])]})
    return {"result": {"debugging_advice": result["messages"][-1].content}}

def give_instructions_node(state: State) -> State:
    result = general_coding_agent.invoke({"messages": [HumanMessage(content=state["query"])]})
    return {"result": {"instructions": result["messages"][-1].content}}

def make_blocks_node(state: State) -> State:
    result = command_agent.invoke({"messages": [state['result']['instructions']]})
    return {"result": {"make_blocks": result["messages"][-1].content}}

def general_agent_node(state: State) -> State:
    result = general_agent.invoke({"messages": [HumanMessage(content=state["query"])]})
    return {"result": {"general_response": result["messages"][-1].content}}


# def format_response(state: State) -> State:
#     result = format_agent.invoke({"messages": [HumanMessage(content=state["result"])]})
#     return {"result": {"formatted_response": result["messages"][-1].content}}
def format_response(state: State) -> State:
    # Extract the actual text content from the result dictionary
    if "result" in state:
        # Get the first value from the inner dictionary
        result_content = next(iter(state["result"].values()))
        
        # Pass the string content to HumanMessage
        result = format_agent.invoke({"messages": [HumanMessage(content=result_content)]})
        return {"result": {"formatted_response": result["messages"][-1].content}}
    return state

graph = StateGraph(State)

# Add nodes
graph.add_node("router", lambda x: x)  # dummy pass-through
graph.add_node("code_explain", code_explain_node)
graph.add_node("give_instructions_2", give_instructions_node)
graph.add_node("code_debugging", code_debugging_node)
graph.add_node("give_instructions", give_instructions_node)
graph.add_node("make_blocks", make_blocks_node)
graph.add_node("format_response", format_response)
graph.add_node("general_agent", general_agent_node)

# Flow: START → router
graph.add_edge(START, "router")

# Conditional routing
graph.add_conditional_edges(
    "router",
    llm_router,
    {
        "code_explain": "code_explain",
        "code_debugging": "code_debugging",
        "give_instructions": "give_instructions",
        "make_blocks": "give_instructions_2",
        "general_agent": "general_agent",
    },
)

# Normal paths
graph.add_edge("code_explain", "format_response")
graph.add_edge("code_debugging", "format_response")
graph.add_edge("give_instructions", "format_response")
graph.add_edge("make_blocks", "format_response")
graph.add_edge("general_agent", "format_response")
graph.add_edge("give_instructions_2", "make_blocks")
# Sequential both path

graph.add_edge("format_response", END)

# Compile
app = graph.compile()
chat_history = []

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat.")
            break

        # scratch_chat_app.send_task("refresh")
        # scratch_chat_app.working_space = get_list_of_used_blocks()
        # scratch_chat_app.context = filter_json()
        # # print(scratch_chat_app.working_space)

        result = app.invoke({
            "query": chat_history + [{"role": "user", "content": user_input}]
        })
        print(result['result']['formatted_response'])
        # for m in result:
        #     if m.type == "ai":  # equivalent to role == "assistant"
        #         pprint.pprint({"Bot": m.content})
