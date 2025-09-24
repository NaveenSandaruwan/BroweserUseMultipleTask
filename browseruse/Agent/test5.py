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
context = filter_json()
dragtool = Toolbox()

general_helper_agent = create_react_agent( 
    model=model,
    tools=[],
    name='general_helper',
    prompt=f'''
    so you are an expert in scratch web application and you can help user to do any task in the scratch web application.
    you can only give answer regarding scratch programming and when the questions are genereic.
    so your goal is to help user to do any task in the scratch web application by following above rules.
    '''
)

context_agent = create_react_agent(
    model=model,
    tools=[],
    name='context_agent',
    prompt=f'''
    You are an expert in understanding and utilizing web page element coordinates.
    what user is doing in the scratch web application: {working_space}

    and you must also be aware of coordinates, beacuse from x=312 to x=972 is the working space.
    so by the x coordinate you can understand where the block is.

    and the blocks are arranged sequentially is given by 1,2,3.... from the working space file.

    '''
)


debugging_agent = create_react_agent(
    model=model,
    tools=[],
    name='debugging_expert',
    prompt=f'''
    You are an expert in debugging Scratch programs.
    Your role is to help users identify and fix issues in their Scratch projects.{working_space}
    You can provide step-by-step guidance on how to troubleshoot common problems,

    use context agent to get the context of the working space and help user to debug their Scratch programs.
    and use gemini to get things users commonly doing mistakes in scratch programming and help user to fix those mistakes.

    '''

)

work_flow = create_supervisor(
    [general_helper_agent, context_agent, debugging_agent],  # Add other agents as needed
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
- Finally get all agents answers and combine them as it is  into a single response to the user.
'''
    )
)









chat_history = []

chat_app = work_flow.compile()


while True:
    user_input = input("User: ")
    send_task("refresh")  
    # print(working_space)
    if user_input.lower() in ["exit", "quit"]:
        break

    result = chat_app.invoke({
        "messages": chat_history + [{"role": "user", "content": user_input}]
    })

    # Extend chat history with LangChain message objects
    chat_history.extend(result["messages"])

    # Print only the last AI message
    ai_messages = [m for m in result["messages"] if m.type == "ai"]
    if ai_messages:
        print("Bot:", ai_messages[-1].content)
        # print(result)



