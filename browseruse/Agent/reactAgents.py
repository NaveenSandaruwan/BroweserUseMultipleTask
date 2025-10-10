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
from tools.execution import AdvancedExecutor

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

old_command_agent_prompt = '''
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

UPDATED_COMMAND_AGENT_PROMPT = '''
You are an ADVANCED Command Agent for Scratch programming with NESTING support.

Your job is to convert instructions into JSON with PLACEMENT and PARENT information.

OUTPUT FORMAT:
{
  "steps": [
    {
      "step": 1,
      "category": "Events",
      "block": "when green flag clicked",
      "placement": "root",
      "parent_step": null
    },
    {
      "step": 2,
      "category": "Control",
      "block": "forever",
      "placement": "below",
      "parent_step": 1
    }
  ]
}

PLACEMENT TYPES:
1. "root" - First block (always an event trigger)
2. "below" - Stack directly below previous block
3. "inside" - Place INSIDE a container block (forever, repeat, if)
4. "condition" - Place in CONDITION slot (diamond/hexagon shape)
5. "outside" - Exit container, return to parent level

PARENT_STEP:
- null: For root blocks
- step_number: Which step this block belongs to or is inside of

BLOCK TYPES YOU MUST KNOW:
- Container blocks (can have blocks inside): forever, repeat times, if then, if then else, repeat until
- Condition blocks (go in diamond slots): touching object, key pressed, mouse down, greater than, less than, equals, and, or, not
- Event blocks (always root): when green flag clicked, when key pressed, when sprite clicked
- Standard blocks: move steps, say, turn, etc.

EXAMPLE 1: "Move sprite if touching mouse pointer"
{
  "steps": [
    {"step": 1, "category": "Events", "block": "when green flag clicked", "placement": "root", "parent_step": null},
    {"step": 2, "category": "Control", "block": "forever", "placement": "below", "parent_step": 1},
    {"step": 3, "category": "Control", "block": "if then", "placement": "inside", "parent_step": 2},
    {"step": 4, "category": "Sensing", "block": "touching object", "placement": "condition", "parent_step": 3},
    {"step": 5, "category": "Motion", "block": "move steps", "placement": "inside", "parent_step": 3}
  ]
}

EXAMPLE 2: "Repeat 5 times: move 10 steps and turn right"
{
  "steps": [
    {"step": 1, "category": "Events", "block": "when green flag clicked", "placement": "root", "parent_step": null},
    {"step": 2, "category": "Control", "block": "repeat times", "placement": "below", "parent_step": 1},
    {"step": 3, "category": "Motion", "block": "move steps", "placement": "inside", "parent_step": 2},
    {"step": 4, "category": "Motion", "block": "turn right", "placement": "inside", "parent_step": 2}
  ]
}

EXAMPLE 3: "Forever: if key pressed then move, else say hello"
{
  "steps": [
    {"step": 1, "category": "Events", "block": "when green flag clicked", "placement": "root", "parent_step": null},
    {"step": 2, "category": "Control", "block": "forever", "placement": "below", "parent_step": 1},
    {"step": 3, "category": "Control", "block": "if then else", "placement": "inside", "parent_step": 2},
    {"step": 4, "category": "Sensing", "block": "key pressed", "placement": "condition", "parent_step": 3},
    {"step": 5, "category": "Motion", "block": "move steps", "placement": "inside", "parent_step": 3},
    {"step": 6, "category": "Looks", "block": "say message", "placement": "inside", "parent_step": 3}
  ]
}

CRITICAL RULES:
1. ALWAYS start with an event block (placement: "root")
2. Blocks that go INSIDE containers use placement: "inside"
3. Condition blocks (touching, key pressed, etc.) use placement: "condition"
4. Track parent_step carefully - it determines nesting
5. Use "outside" to exit a container and return to previous level
6. ALL blocks must have placement and parent_step fields

You MUST output ONLY the JSON object, nothing else.
'''

command_agent = create_react_agent(
    model=model,
    tools=[],
    name="Command_agent",
    prompt=UPDATED_COMMAND_AGENT_PROMPT
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
You are an ADVANCED code fixing expert specializing in Scratch programming with full understanding of NESTING and CONDITION blocks.

You will receive:
1. User's query asking to fix their code
2. Summary of all available Scratch blocks with their functionalities
3. Current workspace state showing blocks and their positions (BROKEN STATE)

YOUR EXPERTISE INCLUDES:
- Understanding container blocks (forever, repeat, if then, if then else, repeat until) that can hold other blocks inside
- Understanding condition blocks (touching, key pressed, greater than, less than, equals, and, or, not) that go in diamond/hexagon slots
- Understanding proper nesting structure and parent-child relationships

ANALYSIS PROCESS:
1. IDENTIFY THE ISSUE:
   - Blocks in wrong order
   - Missing nesting (blocks that should be INSIDE containers but aren't)
   - Missing condition blocks in if/repeat until statements
   - Incorrect placement (condition blocks not in condition slots)
   - Missing event triggers
   - Logical flow errors

2. UNDERSTAND THE INTENT:
   - What is the user trying to achieve?
   - What pattern should the blocks follow?
   - What nesting structure is needed?

3. GENERATE THE FIX with proper structure:

OUTPUT FORMAT - You MUST specify placement and parent relationships:

"To fix your code, we need to restructure the blocks with proper nesting:

Step 1: [Category] - [Block Name] 
   Placement: root (first block, usually an event)
   
Step 2: [Category] - [Block Name]
   Placement: below (stack under previous)
   Parent: Step 1
   
Step 3: [Category] - [Block Name]
   Placement: inside (goes INSIDE a container block)
   Parent: Step 2
   
Step 4: [Category] - [Block Name]
   Placement: condition (goes in diamond/hexagon slot)
   Parent: Step 3
   
Step 5: [Category] - [Block Name]
   Placement: inside (nested inside container)
   Parent: Step 3

[Explain what the fixed structure achieves]"

PLACEMENT TYPES YOU MUST USE:
- "root": First block (always an event trigger)
- "below": Stack directly below previous block
- "inside": Place INSIDE a container block (forever, repeat, if blocks)
- "condition": Place in CONDITION slot (diamond/hexagon shape in if/wait until/repeat until)
- "outside": Exit container, return to parent level

EXAMPLE FIX for "sprite should move when touching mouse":

Current broken state: move block, touching mouse block, if block (all separate)

Fixed structure:
Step 1: Events - when green flag clicked
   Placement: root
   
Step 2: Control - forever
   Placement: below
   Parent: Step 1
   
Step 3: Control - if then
   Placement: inside
   Parent: Step 2
   
Step 4: Sensing - touching mouse pointer
   Placement: condition
   Parent: Step 3
   
Step 5: Motion - move 10 steps
   Placement: inside
   Parent: Step 3

This creates: When flag clicked → Forever loop → If touching mouse → Then move

CRITICAL RULES:
1. Always specify placement type for EVERY step
2. Container blocks MUST have blocks placed "inside" them
3. Condition blocks MUST use placement: "condition" 
4. Track parent relationships carefully
5. Event blocks are always "root"
6. Explain the nesting structure clearly

Remember: The key difference from simple stacking is understanding NESTING - blocks go INSIDE other blocks, not just below them!
'''
)