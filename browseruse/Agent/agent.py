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
from browseruse.Agent.nodes import (
    llm_router,code_explain_node,give_instructions_node,
    code_debugging_node,make_blocks_node,execute_blocks_node,
    format_response,general_agent_node,handle_execution_error,
    code_fixing_node, execute_fix_node, execute_fix_blocks_node 
    )

from reactAgents import add_history_agent

graph = StateGraph(State)

# Add all nodes
# graph.add_node("format_query", format_query)
graph.add_node("router", lambda x: x)
graph.add_node("code_explain", code_explain_node)
graph.add_node("code_debugging", code_debugging_node)
graph.add_node("code_fixing", code_fixing_node)  # NEW
graph.add_node("execute_fix", execute_fix_node)  # NEW
graph.add_node("execute_fix_blocks", execute_fix_blocks_node)  # NEW
graph.add_node("give_instructions", give_instructions_node)
graph.add_node("give_instructions_2", give_instructions_node)
graph.add_node("make_blocks", make_blocks_node)
graph.add_node("execute_blocks", execute_blocks_node)
graph.add_node("format_response", format_response)
graph.add_node("general_agent", general_agent_node)

# Flow: START → router
graph.add_edge(START, "router")

# Conditional routing from router
graph.add_conditional_edges(
    "router",
    llm_router,
    {
        "code_explain": "code_explain",
        "code_debugging": "code_debugging",
        "code_fixing": "code_fixing",  # NEW ROUTE
        "give_instructions": "give_instructions",
        "make_blocks": "give_instructions_2",
        "general_agent": "general_agent",
    },
)

# Code fixing flow: code_fixing → execute_fix → execute_fix_blocks → format_response
graph.add_edge("code_fixing", "execute_fix")
graph.add_edge("execute_fix", "execute_fix_blocks")
graph.add_edge("execute_fix_blocks", "format_response")

# Existing flows

graph.add_edge("code_explain", "format_response")

graph.add_edge("code_debugging", "format_response")

graph.add_edge("give_instructions", "format_response")

graph.add_edge("general_agent", "format_response")


graph.add_edge("give_instructions_2", "make_blocks")
graph.add_edge("make_blocks", "execute_blocks")

# Error handling for execute_blocks
graph.add_conditional_edges(
    "execute_blocks",
    handle_execution_error,
    {
        "make_blocks": "make_blocks",
        "format_response": "format_response",
    },
)

graph.add_edge("format_response", END)

# Compile
chat = graph.compile()

# chat_history = []
# user_input = None
# previous_output = ""

# if __name__ == "__main__":
#     while True:
#         if len(previous_output) > 0:
#             chat_history.append({"User": user_input, "AI agent": add_history_agent.invoke({"messages": previous_output})["messages"][-1].content})
#             user_input = ""
#             previous_output = ""
#             # print(chat_history)
#         user_input = input("You: ")
#         if user_input.lower() in ["exit", "quit"]:
#             print("Exiting chat.")
#             break
#         history = chat_history[-5:] if len(chat_history) > 5 else chat_history
#         conversation = ""
#         if len(history) > 0:
            
#             # Create a formatted conversation string
#             n= 1
#             for turn in history:
#                 conversation += f" Conversation {n}\nUser: {turn['User']}\nAI agent: {turn['AI agent']}\n"
#                 n += 1
#         print("Conversation history:", conversation)

#         result = chat.invoke({
#             "query":  user_input,
#             "chat_history": conversation
#         })

#         previous_output = result['result']['formatted_response']
#         print(previous_output)