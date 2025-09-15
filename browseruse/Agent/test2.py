from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.file_loader import load_and_extract_elements, load_element_descriptions 
from tools.browserUseClient import send_task
from tools.dragTool import Toolbox



GEMINIAPI = os.getenv("GOOGLE_API_KEY") or "AIzaSyBRYRYAjFStLg_xFoNFTaSsaphNuNkmd_I"
# print("GEMINI_API:", GEMINIAPI)  # Debugging line to check if the API key is loaded correctly
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GEMINIAPI,
    temperature=0.7
)


element_expert_agent = create_react_agent(
    model = model,
    tools = [load_and_extract_elements],
    name='element_expert',
    prompt='''You are an expert in extracting and understanding website elements. When the user asks about website elements like explain a block or x,y coordinates, use your tool to extract and provide structured information about them.'''
)

description_expert_agent = create_react_agent(
    model = model,
    tools = [load_element_descriptions],
    name='description_expert',
    prompt='''You are an expert in website element descriptions. When the user asks about descriptions of elements, use your tool to provide detailed and structured explanations.'''
)

drag_tool = Toolbox()

drag_agent = create_react_agent(
    model = model,
    tools = [drag_tool.drag_and_drop],
    name='drag_expert',
    prompt= '''you are a expert in drag and drop operations in the web site. When file expert give knowledge about a element, you can use this tool to perform drag and drop operations on a web page. Always use one tool at a time.'''
)

website_control_agent = create_react_agent(
    model = model,
    tools = [send_task],
    name='website_control_agent',
    prompt= '''You are a world-class expert in web page control. Your job is to perform various actions on a web page using the provided tools. Do not perform any actions outside the scope of web page control.
'''
)

# weather_future_agent = create_react_agent(
#     model = model,
#     tools = [predict_weather_for_date],
#     name='weather_future_agent',
#     prompt= "Get a 5-day weather forecast summary for a city in Sri Lanka. Input should be a city name and date in YYYY-MM-DD format. use this for get present data"
# )




work_flow = create_supervisor(
    [drag_agent, website_control_agent, element_expert_agent, description_expert_agent],
    model=model,
    prompt=(
        'You are a team supervisor managing a drag expert, a website control agent, and an element expert.'
        'First use element_expert_agent to get knowledge about web site elements.'
        'If user ask to explain something, using your knowledge which provided by element_expert_agent and description_expert_agent explain it to the user.'
        'If you understand that user want to perform drag and drop operation, use drag_expert to perform the operation.'
        'Then extract the answer from the expert and return it to the user.'
    )
)


# Chat loop
chat_history = []

chat_app = work_flow.compile()


while True:
    user_input = input("User: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    result = chat_app.invoke({
        "messages": chat_history + [{"role": "user", "content": user_input}]
    })

    # Extend chat history with LangChain message objects
    chat_history.extend(result["messages"])

    # Print assistant reply (check message type safely)
    for m in result["messages"]:
        if m.type == "ai":  # equivalent to role == "assistant"
            print("Bot:", m.content)