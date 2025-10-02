import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
import os
import sys
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END, START
from langchain_core.tools import tool


load_dotenv()

# Import your existing functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from browseruse.Agent.utils.state import State
from browseruse.Agent.nodes import llm_router,code_explain_node,give_instructions_node,code_debugging_node,make_blocks_node,execute_blocks_node,format_response,general_agent_node,handle_execution_error


graph = StateGraph(State)

# Add nodes
graph.add_node("router", lambda x: x)  # dummy pass-through
graph.add_node("code_explain", code_explain_node)
graph.add_node("give_instructions_2", give_instructions_node)
graph.add_node("code_debugging", code_debugging_node)
graph.add_node("give_instructions", give_instructions_node)
graph.add_node("make_blocks", make_blocks_node)
graph.add_node("execute_blocks", execute_blocks_node)
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
graph.add_conditional_edges(
    "execute_blocks",
    handle_execution_error,
    {
        "make_blocks": "make_blocks",
        "format_response": "format_response",
    },
)

# Normal paths
graph.add_edge("code_explain", "format_response")
graph.add_edge("code_debugging", "format_response")
graph.add_edge("give_instructions", "format_response")
graph.add_edge("general_agent", "format_response")
graph.add_edge("give_instructions_2", "make_blocks")
graph.add_edge("make_blocks", "execute_blocks")
# Sequential both path

graph.add_edge("format_response", END)

# Compile
chat = graph.compile()

# chat_history = []

# if __name__ == "__main__":
#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ["exit", "quit"]:
#             print("Exiting chat.")
#             break

#         result = chat.invoke({
#             "query": chat_history + [{"role": "user", "content": user_input}]
#         })
#         print(result['result']['formatted_response'])
       
