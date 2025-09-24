from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
import os
import sys
import json
from dotenv import load_dotenv
from typing import Dict, List, Any


load_dotenv()

# Import your existing functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.file_loader import load_and_extract_elements, load_scratch_descriptions
from tools.browserUseClient import send_task
from tools.dragTool import Toolbox
from tools.filter import filter_json, find_used_blocks, get_list_of_used_blocks, get_category_coordinates, generate_detailed_blocks_summary

# Initialize model
GEMINIAPI = os.getenv("GOOGLE_API_KEY")
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GEMINIAPI,
    temperature=0.3  # Lower temperature for more consistent responses
)


web_application_coding_summary = generate_detailed_blocks_summary(include_all_blocks=True)
working_space = get_list_of_used_blocks()

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

context = filter_json()



# print(web_application_coding_summary)
# print(working_space)

context_agent = create_react_agent(
    model=model,
    tools=[],
    name='coordinate_expert',
    prompt='''
You are an expert in understanding and utilizing web page element coordinates.
 Your role is to help users interact with web pages effectively by leveraging the provided coordinate information.
 Here is the context you can use(each elment have this firmat 'tag_name': 'text', 'text_content': 'move', 'x': 74, 'y': 149 ):
        if your provided text have "move" block add this context (X: 74, Y: 149 ) to the "move" block.

        All content seen in the page:
      {context}
    Your tasks include: 
     - Analyse other agent responses and add position context to related Scratch blocks if needed.
     - Finally Add position context to related Scratch blocks.

'''
)

dragtool = Toolbox()



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






drag_and_drop_agent = create_react_agent(
    model=model,
    tools=[dragtool.drag_and_drop],
    name='drag_and_drop_expert',
    prompt='''
You are a drag-and-drop expert for web applications, specializing in arranging Scratch code blocks using the drag_and_drop tool.

When a user requests a drag-and-drop operation, follow these steps:

1. Review the current workspace state: {working_space}
   - This shows which blocks are already in the workspace and their coordinates.
   - Identify the destination positions using these data.

2. Review the available blocks: {context}
   - This lists all blocks you can use, along with their names and positions on the page.
   - Identify the source positions using these data. as a example you can see information in this format:
    {'tag_name': 'text', 'text_content': 'move', 'x': 74, 'y': 149 }

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



# research_agent= create_react_agent(
#     model = model,
#     tools = [search_ddgo],
#     name='search_expert',
#     prompt= 'you are a world class researcher with access to web search. Do not do any math'
# )

# weather_agent= create_react_agent(
#     model = model,
#     tools = [get_weather],
#     name='weather_expert',
#     prompt= '''You are a world-class weather researcher with access to real-time weather data through web services. Your job is to provide accurate, concise, and up-to-date weather reports for any location requested. Do not perform any calculations or estimates manually. Just retrieve and present verified information.

# - Use plain language that is easy for anyone to understand.
# - Always mention temperature, humidity, wind speed, and general weather conditions.
# - If the city is not found or there’s an error, politely explain that the data is unavailable.
# - Keep your response factual and avoid unnecessary elaboration.
# '''
# )

# weather_future_agent = create_react_agent(
#     model = model,
#     tools = [predict_weather_for_date],
#     name='weather_future_agent',
#     prompt= "Get a 5-day weather forecast summary for a city in Sri Lanka. Input should be a city name and date in YYYY-MM-DD format. use this for get present data"
# )

# crop_expert = create_react_agent(
#     model = model,
#     tools = [get_suitable_crops_only],
#     name='crop_expert', 
#     prompt= 'you are a crop expert. Use this tool to get suitable crops for a given location. '

# )

work_flow = create_supervisor(
    [general_coding_agent, context_agent, debugging_agent],  # Add other agents as needed
    model=model,
    prompt=(
        '''
You are an expert supervisor overseeing a team of specialized agents which are coding_expert, context_expert, debugging_expert, and drag_and_drop_expert. Your role is to:
- Give instruction only regarding Scratch programming.

- Do not ask many questions from the user. Try to understand the user query and delegate it to the best agent.
- Analyze user queries and determine which agent is best suited to respond.
- Delegate tasks to the appropriate agent based on their expertise.
- Ensure that responses are accurate, relevant, and concise.
- If a query involves multiple topics, break it down and assign each part to the relevant agent.
- Maintain a coherent and user-friendly conversation flow.

Here are the agents you can delegate to:
       - coding_expert: Specializes in Scratch programming and can provide detailed explanations of Scratch blocks and their usage.
       - context_expert: Specializes in understanding and utilizing web page contexts element coordinates, particularly for Scratch programming interface.
       - debugging_expert: Specializes in analyzing the user's Scratch workspace to identify issues, provide feedback, and suggest improvements.

work flow do not deviate from these steps, please follow these:
- First, analyze the user query and determine the most suitable agent based on the query.
- If the user query indicates they need help identifying issues or fixing their Scratch program (e.g., "Am I doing something wrong?", "Can you fix this?", "How to do this correctly?"), delegate the task to the debugging_expert.
- Before you give the final answer to the user, make sure to check if you have enough context about the Scratch programming interface. If not, use the context_expert agent to get the necessary coordinates information and add those to the relevant Scratch blocks.

- Finally get all agents answers and combine them as it is  into a single response to the user.
- Finally get all agents answers and combine them as it is  into a single response to the user.
'''
    )
)

# work_flow = create_supervisor(
#     [general_coding_agent,context_agent],  # Add other agents as needed
#     model=model,
#     prompt=(
#         '''
# You are an expert supervisor overseeing a team of specialized agents which are coding_expert, context_expert, and drag_and_drop_expert. Your role is to:
# - Give instruction only regarding Scratch programming.

# - Do not ask many questions from the user. Try to understand the user query and delegate it to the best agent.
# - Analyze user queries and determine which agent is best suited to respond.
# - Delegate tasks to the appropriate agent based on their expertise.
# - Ensure that responses are accurate, relevant, and concise.
# - If a query involves multiple topics, break it down and assign each part to the relevant agent.
# - Maintain a coherent and user-friendly conversation flow.

# Here are the agents you can delegate to:
#        - coding_expert: Specializes in Scratch programming and can provide detailed explanations of Scratch blocks and their usage.
#        - context_expert: Specializes in understanding and utilizing web page contexts element coordinates, particularly for Scratch programming interface.
       
# work flow do not deviate form these steps please follow these,
# - first get answer by most suitable agent based on user quwery.
# - Before you give the final answer to the user, make sure to check if you have enough context about the Scratch programming interface. If not, use the coordinate_expert agent to get the necessary coordinates information and add those to the relevant Scratch blocks.

# - Finally get all agents answers and combine them as it is  into a single response to the user.
# - Finally get all agents answers and combine them as it is  into a single response to the user.
# '''
       
#     )
# )


# Chat loop
chat_history = []

chat_app = work_flow.compile()


def call_LLM(user_input):
    send_task("refresh")  

    result = chat_app.invoke({
        "messages": chat_history + [{"role": "user", "content": user_input}]
    })

    # Extend chat history with LangChain message objects
    chat_history.extend(result["messages"])

    # Print only the last AI message
    ai_messages = [m for m in result["messages"] if m.type == "ai"]
    if ai_messages:
        print(ai_messages)
        return("Bot:", ai_messages[-1].content)
        # print(result)