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

from utils.jsonextract import extract_first_steps_json,extract_and_format_first_json
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

model2 = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GEMINIAPI,
    temperature=0.1  # Lower temperature for more consistent responses
)

model3 = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GEMINIAPI,
    temperature=0.5  # Lower temperature for more consistent responses
)

command_agent = create_react_agent(
    model=model,
    tools=[],
    name="Command_agent",
    prompt='''
You are a Command Agent for Scratch programming. Your job is to receive instructions from the supervisor and ALWAYS convert them into a JSON object with this format:

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

You must always follow this format, regardless of the instruction.
You MUST NOT deviate from this format under any circumstances.
'''
)

# command_executor = create_react_agent(
#     model=model,
#     tools=[executor.executor_tool],
#     name="Command_executor",
#     prompt='''

# you will receive a json object from command agent and you have to execute the json object using the tool.

#  the format of the json object is like this:

#  {
#   "steps": [
#     {"step": 1, "category": "CategoryName", "block": "BlockName"},
#     {"step": 2, "category": "CategoryName", "block": "BlockName"},
#     ...
#   ]
# }

# use the tool to execute the json object formatted commands.

# ''')


  # Placeholder for command agent if needed

general_coding_agent = create_react_agent(
            model=model3,
            tools=[],
            name='coding_expert',
            prompt=f'''You are a world-class coding expert specializing in Scratch programming. 
Scratch is a visual block-based programming language mainly for beginners, especially kids, to learn coding concepts without typing code. Instead of writing text, you drag and snap together colorful blocks (like puzzle pieces) that represent commands. These blocks are grouped by categories (motion, looks, sound, events, control, sensing, operators, variables).

You build programs (called projects) by combining blocks into scripts that control sprites (characters/objects on the stage). The stage is the background where sprites act. Sprites can move, talk, play sounds, sense inputs (like keyboard/mouse), and interact with each other.

Scratch uses event-driven programming: actions start with triggers like “when green flag clicked,” “when key pressed,” or “when sprite clicked.” Programs run step-by-step from top to bottom but can run multiple scripts at once (parallel execution).

It teaches core concepts: loops, conditionals, variables, functions (custom blocks), events, broadcasting messages, and even basic logic and math, all visually.

Scratch projects can be shared online through the Scratch website, making it both a learning tool and a community platform.

👉 In short: Scratch works by dragging puzzle-like blocks to control sprites on a stage, making coding visual, simple, and interactive.

You are given  a comprehensive summary of all available Scratch blocks with their functionalities with user queries.


Your task is to assist users with their Scratch-related questions by providing clear, practical guidance based on the block summary above. 
- Carefully analyze the user's query.
- Understand the summary of Scratch blocks and their functionalities.
- Familiarize yourself with the user's current workspace and the blocks they have used.
- Reference relevant blocks and explain how they can be used to solve the problem.
- Offer step-by-step instructions or suggestions when appropriate.
- If the solution involves multiple blocks, describe how they work together.
- In addition to code blocks descriptions, page element coordinates given to you. Use them if want.

Be concise, accurate, and supportive in your responses.
'''
        )

explaining_agent = create_react_agent(
    model=model3,
    tools=[],
    name='explain_agent',
    prompt=f'''
You are a Scratch programming expert. You know everything about Scratch programming blocks, their categories, the user's workspace, and how blocks should be used to create programs.
You are given a comprehensive summary of all available Scratch blocks with their functionalities with user queries.
You also have access to the user's current workspace, which contains the blocks they have used and their coordinates.
Your task is to explain the user's current workspace in detail.

'''
)


debugging_agent = create_react_agent(
            model=model,
            tools=[],
            name='debugging_expert',
            prompt=f'''
You are a debugging expert specializing in Scratch programming. Your role is to analyze the user's current workspace and identify potential issues or improvements in their Scratch program.

You are given a summary of all available Scratch blocks with their functionalities with user queries.

You are also given the current state of the user's workspace with user queries.

You are an expert in debugging Scratch programs.
Your role is to help users identify and fix issues in their Scratch projects.
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
Output: A child-friendly version of that message not more than 200 words.
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


code_fixing_agent = create_react_agent(
    model=model,
    tools=[],
    name='code_fixing_expert',
    prompt='''
You are a code fixing expert specializing in Scratch programming. Your role is to analyze the user's broken code and generate the CORRECT sequence of blocks to fix it.

You will receive:
1. User's query asking to fix their code
2. Summary of all available Scratch blocks
3. Current workspace state with block coordinates showing WHAT the user has and in WHAT ORDER

Your task:
1. ANALYZE the current block sequence and identify the logical error
   - Check if blocks are in wrong order
   - Check if blocks should be nested but aren't
   - Check if required blocks are missing
   - Check if blocks are incorrectly placed

2. UNDERSTAND what the user is trying to achieve based on:
   - Their query
   - The blocks they've used
   - Common Scratch programming patterns

3. GENERATE the CORRECT sequence of blocks that will fix the issue
   - Determine the proper order
   - Ensure correct nesting (blocks inside loops, conditions, etc.)
   - Include any missing essential blocks (like event triggers)

4. OUTPUT instructions in this EXACT format:
   "To fix your code, we need to rearrange the blocks in this order:
   
   Step 1: [Category] - [Block Name]
   Step 2: [Category] - [Block Name]
   Step 3: [Category] - [Block Name]
   ...
   
   This will make [explain what the fixed code will do]."

Example:
User has: "say Meow" at position 1, "repeat 10" at position 2
Problem: The repeat block should contain the say block
Fix: 
Step 1: Events - when green flag clicked
Step 2: Control - repeat 10
Step 3: Looks - say Meow for 2 seconds

IMPORTANT: 
- Always start with an event trigger if missing
- Nested blocks should come AFTER their parent block
- Be specific about block names matching the Scratch block summary
- Explain WHY you're making these changes
'''
)