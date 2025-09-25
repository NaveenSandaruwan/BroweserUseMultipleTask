from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
import os
import sys
import json
from dotenv import load_dotenv
from typing import Dict, List, Any

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.file_loader import load_and_extract_elements, load_scratch_descriptions
from tools.browserUseClient import send_task
from tools.dragTool import Toolbox
from tools.filter import filter_json, find_used_blocks, get_list_of_used_blocks, get_category_coordinates, generate_detailed_blocks_summary


class ScratchChatApp:
    def __init__(self):

        self.send_task = send_task

        GEMINIAPI = os.getenv("GOOGLE_API_KEY")
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=GEMINIAPI,
            temperature=0.3
        )

        self.web_application_coding_summary = generate_detailed_blocks_summary(include_all_blocks=True)
        self.working_space = get_list_of_used_blocks()
        self.context = filter_json()

        self.general_coding_agent = create_react_agent(
            model=self.model,
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

{self.web_application_coding_summary}

Your task is to assist users with their Scratch-related questions by providing clear, practical guidance based on the block summary above. 
- Carefully analyze the user's query.
- Reference relevant blocks and explain how they can be used to solve the problem.
- Offer step-by-step instructions or suggestions when appropriate.
- If the solution involves multiple blocks, describe how they work together.
- In addition to code blocks descriptions, page element coordinates given to you. Use them if want.

Be concise, accurate, and supportive in your responses.
'''
        )

        self.context_agent = create_react_agent(
            model=self.model,
            tools=[],
            name='coordinate_expert',
            prompt=f'''
You are an expert in understanding and utilizing web page element coordinates.
 Your role is to help users interact with web pages effectively by leveraging the provided coordinate information.
 Here is the context you can use(each elment have this firmat 'tag_name': 'text', 'text_content': 'move', 'x': 74, 'y': 149 ):
        if your provided text have "move" block add this context (X: 74, Y: 149 ) to the "move" block.

        All content seen in the page:
      {self.context}
    Your tasks include: 
     - Analyse other agent responses and add position context to related Scratch blocks if needed.
     - Finally Add position context to related Scratch blocks.

You are an expert in understanding and utilizing web page element coordinates.
what user is doing in the scratch web application: {self.working_space}

and you must also be aware of coordinates, beacuse from x=312 to x=972 is the working space.
so by the x coordinate you can understand where the block is.

and the blocks are arranged sequentially is given by 1,2,3.... from the working space file.     

'''
        )

        dragtool = Toolbox()

        self.debugging_agent = create_react_agent(
            model=self.model,
            tools=[],
            name='debugging_expert',
            prompt=f'''
You are a debugging expert specializing in Scratch programming. Your role is to analyze the user's current workspace and identify potential issues or improvements in their Scratch program.

Here is the summary of all available Scratch blocks:
{self.web_application_coding_summary}

Here is the current state of the user's workspace:
{self.working_space}

You are an expert in debugging Scratch programs.
Your role is to help users identify and fix issues in their Scratch projects.{self.working_space}
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

        self.drag_and_drop_agent = create_react_agent(
            model=self.model,
            tools=[dragtool.drag_and_drop],
            name='drag_and_drop_expert',
            prompt=f'''
You are a drag-and-drop expert for web applications, specializing in arranging Scratch code blocks using the drag_and_drop tool.

When a user requests a drag-and-drop operation, follow these steps:

1. Review the current workspace state: {self.working_space}
   - This shows which blocks are already in the workspace and their coordinates.
   - Identify the destination positions using these data.

2. Review the available blocks: {self.context}
   - This lists all blocks you can use, along with their names and positions on the page.
   - Identify the source positions using these data. as a example you can see information in this format:
    {{'tag_name': 'text', 'text_content': 'move', 'x': 74, 'y': 149 }}

3. Understand the user's request:
   - Identify which block(s) the user wants to move and where they should be placed.
   - Use the available blocks and workspace information to determine the source and destination coordinates.

4. Use the drag_and_drop tool to perform the operation:
   - To add a block to the start of the workspace, use the workspace's starting coordinates.
   - To insert a block after another block, use the coordinates of the target block as the destination.
   - Example: drag_and_drop(source_x, source_y, dest_x, dest_y)

5. Repeat as needed for multiple blocks or steps, updating your understanding of the workspace after each operation.

Always ensure your actions match the user's intent and the current state of the workspace.
Return a confirmation message after completing the drag-and-drop operation with coordinates which start from the source block and end at the destination block.
'''
        )

        self.format_agent = create_react_agent(
            model=self.model,
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

        self.work_flow = create_supervisor(
            [self.general_coding_agent, self.context_agent, self.debugging_agent, self.format_agent],
            model=self.model,
            prompt=(
                '''
You are an expert supervisor overseeing a team of specialized agents which are coding_expert, context_expert, debugging_expert, and drag_and_drop_expert. Your role is to:
- Give instruction only regarding Scratch programming.
- Finally get all agents answers and combine them as it is  into a single response using format_agent to the user.
- Do not ask many questions from the user. Try to understand the user query and delegate it to the best agent.
- Analyze user queries and determine which agent is best suited to respond.
- Delegate tasks to the appropriate agent based on their expertise.
- If a query involves multiple topics, break it down and assign each part to the relevant agent.


Here are the agents you can delegate to:
       - coding_expert: Specializes in Scratch programming and can provide detailed explanations of Scratch blocks and their usage.
       - context_expert: Specializes in understanding and utilizing web page contexts element coordinates, particularly for Scratch programming interface.
       - debugging_expert: Specializes in analyzing the user's Scratch workspace to identify issues, provide feedback, and suggest improvements.
       - debugging_expert: Specializes to see the user workspace and identify issues, provide feedback, and suggest improvements.
       - format_agent: Specializes in reformatting technical Scratch programming instructions into simple, clear, and fun explanations suitable for children.

work flow do not deviate from these steps, please follow these:
- First, analyze the user query and determine the most suitable agent based on the query.
- If the user query indicates they need help identifying issues or fixing their Scratch program (e.g., "Am I doing something wrong?", "Can you fix this?", "How to do this correctly?"), delegate the task to the debugging_expert.
- Before you give the final answer to the user, make sure to check if you have enough context about the Scratch programming interface. If not, use the context_expert agent to get the necessary coordinates information and add those to the relevant Scratch blocks.

Important:
- Finally get all agents answers and combine them as it is  into a single response using format_agent to the user.
- Finally get all agents answers and combine them as it is  into a single response using format_agent to the user.
'''
            )
        )

        self.chat_history = []
    def invoke(self, user_input):
        self.send_task("refresh")
        # Check if user_input is a string or dictionary
        if isinstance(user_input, str):
            messages = self.chat_history + [{"role": "user", "content": user_input}]
        else:
            # We're already getting a properly formatted input
            print("Warning: Expected string input. Using provided input structure.")
            messages = user_input.get("messages", [])
            
        result = self.work_flow.compile().invoke({
            "messages": messages
        })
        self.chat_history.extend(result["messages"])

        return result


# Create an instance of the class
scratch_chat_app = ScratchChatApp()

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat.")
            break

        scratch_chat_app.send_task("refresh")
        scratch_chat_app.working_space = get_list_of_used_blocks()
        scratch_chat_app.context = filter_json()
        print(scratch_chat_app.working_space)

        result = scratch_chat_app.invoke({
            "messages": scratch_chat_app.chat_history + [{"role": "user", "content": user_input}]
        })

        # Store responses by agent name
        responses = {
            "supervisor": None,
            "format_agent": None,
            "coordinate_expert": None,
            "debugging_expert": None,
            "coding_expert": None
        }

        for message in result["messages"]:
            # AI/Tool messages will have .name
            if hasattr(message, "name") and message.name in responses:
                responses[message.name] = message.content

        # Check if format agent has a result
        if responses["format_agent"] and len(responses["format_agent"]) > 200:
            print("Bot:", responses["format_agent"])
        else:
            # Pick the longest response among other agents
            longest_response = max(
                (resp for role, resp in responses.items() if role != "format_agent" and resp),
                key=len,
                default=None
            )
            if longest_response:
                print("Bot:", longest_response)
            else:
                ai_messages = [m for m in result["messages"] if m.type == "ai"]
                if ai_messages:
                    print("Bot:", ai_messages[-1].content)
                else:
                    print("Bot: (No response found)")
