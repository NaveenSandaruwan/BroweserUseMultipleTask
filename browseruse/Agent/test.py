import os, sys, json
from typing import Annotated
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import Command
from langchain_core.tools import tool,  InjectedToolCallId
from langgraph.prebuilt import InjectedState

# --- Load environment ---
load_dotenv()

# --- Model ---
GEMINIAPI = os.getenv("GOOGLE_API_KEY")
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GEMINIAPI,
    temperature=0.3
)

# --- Your imports ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from utils.file_loader import load_and_extract_elements, load_scratch_descriptions
from tools.browserUseClient import send_task
from tools.dragTool import Toolbox
from tools.filter import filter_json, find_used_blocks, get_list_of_used_blocks, get_category_coordinates, generate_detailed_blocks_summary

# --- Context & summaries ---
web_application_coding_summary = generate_detailed_blocks_summary(include_all_blocks=True)
working_space = get_list_of_used_blocks()
context = filter_json()



from langchain.schema import AIMessage

def collect_all_agent_messages(state: MessagesState):
    """
    Collect the last AI message from each agent (supervisor + experts).
    Excludes collector + format_agent itself.
    Labels each agent with its name so the format_agent knows the source.
    """
    messages = state.get("messages", [])

    # Filter relevant AI messages
    agent_msgs = [
        m for m in messages
        if isinstance(m, AIMessage)
        and getattr(m, "name", None) not in (None, "collector", "format_agent")
        and m.content and str(m.content).strip()
    ]

    # Keep only the last message per agent
    last_by_agent = {}
    for m in agent_msgs:
        agent_name = getattr(m, "name", "unknown_agent")
        last_by_agent[agent_name] = m  # overwrite ensures "last seen" survives

    # Wrap them with labels
    labeled_msgs = []
    for agent_name, m in last_by_agent.items():
        labeled_text = f"[{agent_name}] {m.content}"
        labeled_msgs.append(AIMessage(content=labeled_text, name="collector"))

    # Debug
    print("Collector gathered last outputs:", [(m.name, m.content) for m in labeled_msgs])

    return {"messages": labeled_msgs}


# --- Agents ---
coding_agent = create_react_agent(
    model=model,
    tools=[],
    name="coding_expert",
    prompt=f"""You are a world-class coding expert specializing in Scratch programming. 
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
"""
)

context_agent = create_react_agent(
    model=model,
    tools=[],
    name="context_expert",
    prompt=f"""
You are an expert in understanding and utilizing web page element coordinates.
 Your role is to help users interact with web pages effectively by leveraging the provided coordinate information.
 Here is the context you can use(each elment have this firmat 'tag_name': 'text', 'text_content': 'move', 'x': 74, 'y': 149 ):
        if your provided text have "move" block add this context (X: 74, Y: 149 ) to the "move" block.

        All content seen in the page:
      {context}
    Your tasks include: 
     - Analyse other agent responses and add position context to related Scratch blocks if needed.
     - Finally Add position context to related Scratch blocks.
"""
)

debugging_agent = create_react_agent(
    model=model,
    tools=[],
    name="debugging_expert",
    prompt=f"""
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
"""
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

# ...existing code...

# Delegation tools (handoff)
@tool
def transfer_to_coding_expert(state: Annotated[MessagesState, InjectedState],
                              tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    
    ''' Tool to transfer control to the coding expert agent '''

    tool_msg = {"role": "tool", "content": "handoff to coding_expert",
                "name": "transfer_to_coding_expert", "tool_call_id": tool_call_id}
    return Command(goto="coding_expert",
                   update={**state, "messages": state["messages"] + [tool_msg]},
                   graph=Command.PARENT)

@tool
def transfer_to_context_expert(state: Annotated[MessagesState, InjectedState],
                               tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    ''' Tool to transfer control to the context expert agent '''

    tool_msg = {"role": "tool", "content": "handoff to context_expert",
                "name": "transfer_to_context_expert", "tool_call_id": tool_call_id}
    return Command(goto="context_expert",
                   update={**state, "messages": state["messages"] + [tool_msg]},
                   graph=Command.PARENT)

@tool
def transfer_to_debugging_expert(state: Annotated[MessagesState, InjectedState],
                                  tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    ''' Tool to transfer control to the debugging expert agent '''
    tool_msg = {"role": "tool", "content": "handoff to debugging_expert",
                "name": "transfer_to_debugging_expert", "tool_call_id": tool_call_id}
    return Command(goto="debugging_expert",
                   update={**state, "messages": state["messages"] + [tool_msg]},
                   graph=Command.PARENT)


# --- Supervisor Agent ---
supervisor_agent = create_react_agent(
    model=model,
    tools=[transfer_to_coding_expert, transfer_to_context_expert, transfer_to_debugging_expert],
    name="supervisor",
    prompt="""
You are an expert supervisor overseeing a team of specialized agents which are coding_expert, context_expert, debugging_expert, and drag_and_drop_expert. Your role is to:
- Give instruction only regarding Scratch programming.
Important:
- Finally get all agents answers and combine them as it is  into a single response to the user.

- Do not ask many questions from the user. Try to understand the user query and delegate it to the best agent.
- Analyze user queries and determine which agent is best suited to respond.
- Delegate tasks to the appropriate agent based on their expertise.
- Ensure that responses are accurate, relevant, and concise.
- If a query involves multiple topics, break it down and assign each part to the relevant agent.
- Maintain a coherent and user-friendly conversation flow.

Here are the agents you can delegate to:
       - coding_expert: Specializes in Scratch programming and can provide detailed explanations of Scratch blocks and their usage.
       - context_expert: Specializes in understanding and utilizing web page contexts element coordinates, particularly for Scratch programming interface.
       - debugging_expert:Know the users workspace well. Specializes in analyzing the user's Scratch workspace to identify issues, provide feedback, and suggest improvements.

       
work flow do not deviate from these steps, please follow these:
- First, analyze the user query and determine the most suitable agent based on the query.
- If the user query indicates they need help identifying issues or fixing their Scratch program (e.g., "Am I doing something wrong?", "Can you fix this?", "How to do this correctly?"), delegate the task to the debugging_expert.
- Before you give the final answer to the user, make sure to check if you have enough context about the Scratch programming interface. If not, use the context_expert agent to get the necessary coordinates information and add those to the relevant Scratch blocks.

Important:
- Finally get all agents answers and combine them as it is  into a single response to the user.
- Finally get all agents answers and combine them as it is  into a single response to the user.
"""
)
builder = StateGraph(MessagesState)

# Add nodes
builder = builder.add_node("supervisor", supervisor_agent)
builder = builder.add_node("coding_expert", coding_agent)
builder = builder.add_node("context_expert", context_agent)
builder = builder.add_node("debugging_expert", debugging_agent)
builder = builder.add_node("collector", collect_all_agent_messages)  # 👈 collector
# builder = builder.add_node("format_agent", format_agent)

# Flow
builder = builder.add_edge(START, "supervisor")
builder = builder.add_edge("coding_expert", "supervisor")
builder = builder.add_edge("context_expert", "supervisor")
builder = builder.add_edge("debugging_expert", "supervisor")

# Supervisor → Collector → Format Agent → END
builder = builder.add_edge("supervisor", "collector")
builder = builder.add_edge("collector", "format_agent")
builder = builder.add_edge("format_agent", END)

graph = builder.compile()

chat_history = []
# while True:
#     user_input = input("User: ")
#     send_task("refresh")
#     if user_input.lower() in ["exit", "quit"]:
#         break
#     if len(chat_history) > 5:
#         chat_history = chat_history[-5:]  # keep only last 5 messages
#     result = graph.invoke({
#         "messages": chat_history + [{"role": "user", "content": user_input}]
#     })

#     chat_history.extend(result["messages"])

    
#     format_messages = [
#         m for m in result["messages"]
#         if m.type == "ai" and m.name == "format_agent" and m.content and m.content.strip()
#     ]

#     if format_messages:
#         # take the last non-empty message from format_agent
#         last_format_message = format_messages[-1]
#         print("Bot:", last_format_message.content)
#     else:
#         print("Bot: (no respons from format agent)")

def call_LLM(user_input):
            send_task("refresh")
            result = graph.invoke({
                "messages": chat_history + [{"role": "user", "content": user_input}]
            })
            chat_history.extend(result["messages"])

            format_messages = [
                m for m in result["messages"]
                if m.type == "ai" and m.name == "format_agent" and m.content and m.content.strip()
            ]

            if result:
                # take the last non-empty message from format_agent
                # last_format_message = result[-1]
                print("Bot:", result)
            else:
                print("Bot: (no respons from format agent)")

# def call_LLM(user_input):
#             send_task("refresh")
#             result = graph.invoke({
#                 "messages": chat_history + [{"role": "user", "content": user_input}]
#             })
#             chat_history.extend(result["messages"])

#             format_messages = [
#                 m for m in result["messages"]
#                 if m.type == "ai" and m.name == "format_agent" and m.content and m.content.strip()
#             ]

#             if format_messages:
#                 last_format_message = format_messages[-1]
#                 print("Bot:", last_format_message.content)
#                 return last_format_message.content
#             else:
#                 print("Bot: (no respons from format agent)")
#                 return None
            
# print("LLM is ready to use..."+"\n" ,call_LLM("Hello!"))