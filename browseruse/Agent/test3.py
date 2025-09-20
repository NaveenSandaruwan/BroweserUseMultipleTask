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

# Initialize drag tool
drag_tool = Toolbox()


def get_workspace_blocks():
    """
    Get all blocks currently in the workspace with their positions.
    Returns only blocks that are being used (x > 310).
    """
    try:
        used_blocks = find_used_blocks()
        if not used_blocks:
            return {"workspace_blocks": [], "message": "No blocks in workspace yet"}
        
        formatted_blocks = []
        for i, block in enumerate(used_blocks, 1):
            formatted_blocks.append({
                "number": i,
                "name": block['text_content'],
                "position": {"x": block['x'], "y": block['y']},
                "description": f"Block #{i}: {block['text_content']} at ({block['x']}, {block['y']})"
            })
        
        return {
            "workspace_blocks": formatted_blocks,
            "total_blocks": len(formatted_blocks),
            "message": "These are the blocks currently in your workspace"
        }
    except Exception as e:
        return {"error": str(e), "workspace_blocks": []}

def get_category_info(category_name: str = None):
    """
    Get information about Scratch categories and their blocks.
    If category_name is provided, returns detailed info for that category.
    """
    try:
        with open(os.getenv("ELEMENTS_DESCRIPTION_JSON_PATH"), 'r') as f:
            data = json.load(f)
        
        if category_name:
            # Find matching category (case-insensitive)
            for cat, info in data.items():
                if cat.lower() == category_name.lower():
                    return {
                        "category": cat,
                        "position": info['coordinates'],
                        "blocks": info.get('blocks', []),
                        "block_count": len(info.get('blocks', [])),
                        "message": f"{cat} category has {len(info.get('blocks', []))} blocks"
                    }
            return {"error": f"Category '{category_name}' not found"}
        else:
            # Return summary of all categories
            categories = {}
            for cat, info in data.items():
                categories[cat] = {
                    "position": info['coordinates'],
                    "block_count": len(info.get('blocks', []))
                }
            return {
                "categories": categories,
                "message": "Here are all the Scratch categories available"
            }
    except Exception as e:
        return {"error": str(e)}

def get_block_position(block_name: str):
    """
    Find the exact position of a specific block by name.
    Searches both in categories and workspace.
    """
    # First check workspace blocks
    workspace = get_workspace_blocks()
    if workspace.get('workspace_blocks'):
        for block in workspace['workspace_blocks']:
            if block_name.lower() in block['name'].lower():
                return {
                    "found": True,
                    "location": "workspace",
                    "block_name": block['name'],
                    "position": block['position'],
                    "message": f"Found '{block['name']}' in workspace at ({block['position']['x']}, {block['position']['y']})"
                }
    
    # Check in category panels
    filtered = filter_json()
    for item in filtered:
        if block_name.lower() in item['text_content'].lower():
            return {
                "found": True,
                "location": "category_panel",
                "block_name": item['text_content'],
                "position": {"x": item['x'], "y": item['y']},
                "message": f"Found '{item['text_content']}' in category panel at ({item['x']}, {item['y']})"
            }
    
    return {
        "found": False,
        "message": f"Could not find block '{block_name}'"
    }

def format_child_response(content: str, position_data: Dict = None):
    """
    Format responses in a child-friendly way with position data if available.
    """
    # Child-friendly formatting
    friendly_terms = {
        "coordinate": "spot",
        "position": "place", 
        "execute": "do",
        "implement": "make",
        "utilize": "use",
        "algorithm": "steps"
    }
    
    formatted_content = content
    for formal, friendly in friendly_terms.items():
        formatted_content = formatted_content.replace(formal, friendly)
    
    # Add position information if available
    if position_data:
        position_info = f"\n\n📍 Position info: "
        if isinstance(position_data, dict):
            if 'x' in position_data and 'y' in position_data:
                position_info += f"This is at spot ({position_data['x']}, {position_data['y']})"
            elif 'position' in position_data:
                pos = position_data['position']
                position_info += f"This is at spot ({pos.get('x', '?')}, {pos.get('y', '?')})"
        formatted_content += position_info
    
    return formatted_content



# 1. Code Helper Agent - Answers questions about making code
code_helper_agent = create_react_agent(
    model=model,
    tools=[get_category_info, get_block_position],
    name='code_helper',
    prompt='''You are a friendly Scratch coding helper for children. Your job is to help them understand how to make programs.

    When a child asks about making code:
    1. Use get_category_info to show them which categories have the blocks they need
    2. Explain in simple, fun terms how to combine blocks
    3. Always include the position of relevant categories
    
    Keep explanations short and use simple words. Be encouraging!
    Example: "To make your sprite move, look at the Motion category at (x:1, y:93)! You can find the 'move steps' block there!"
    
    ALWAYS include positions when mentioning categories or blocks.'''
)

# 2. Code Checker Agent - Validates user's code
code_checker_agent = create_react_agent(
    model=model,
    tools=[get_workspace_blocks, get_category_info],
    name='code_checker',
    prompt='''You are a friendly code checker for children using Scratch. 

    When checking if code is correct:
    1. Use get_workspace_blocks to see what blocks they've used
    2. Check if the blocks make sense together
    3. Give friendly suggestions if something could be better
    
    Be encouraging! Even if something is wrong, praise what they did right first.
    Example: "Great job using the move block! It's at position (320, 150). To make it work better, try adding a 'when green flag clicked' block at the top!"
    
    ALWAYS mention block positions when discussing specific blocks.'''
)

# 3. Navigator Agent - Handles UI navigation
navigator_agent = create_react_agent(
    model=model,
    tools=[send_task, get_block_position, get_category_info],
    name='navigator',
    prompt='''You are a navigation helper for the Scratch interface.

    When the user wants to navigate or click something:
    1. First identify what element they want using get_block_position or get_category_info
    2. Get the exact position
    3. Use send_task with clear instructions including coordinates
    
    Example task format for send_task:
    - "Click on Motion category at position (1, 93)"
    - "Click on the move block at (15, 120)"
    
    Always confirm the action after sending the task.'''
)

# 4. Drag Drop Agent - Handles drag and drop operations
drag_drop_agent = create_react_agent(
    model=model,
    tools=[drag_tool.drag_and_drop, get_block_position],
    name='drag_drop',
    prompt='''You are the drag and drop specialist for Scratch blocks.

    When asked to move blocks:
    1. Use get_block_position to find the source block
    2. Determine the target position (usually the workspace area)
    3. Use drag_and_drop with exact coordinates
    
    Remember:
    - Blocks in categories have x < 310
    - Workspace blocks have x > 310
    - Always verify positions before dragging'''
)

# 5. Response Formatter Agent - Makes everything child-friendly
formatter_agent = create_react_agent(
    model=model,
    tools=[format_child_response],
    name='formatter',
    prompt='''You format all responses to be perfect for children aged 8-12.

    Rules:
    1. Use simple, fun language
    2. Include emojis sparingly (🎮 ⭐ 👍 🚀)
    3. Keep sentences short
    4. Always include position information in a friendly way
    5. Be encouraging and positive
    
    Example: "Awesome! 🌟 Your move block is at spot (320, 150). That's perfect for making your sprite dance!"'''
)


supervisor = create_supervisor(
    [code_helper_agent, code_checker_agent, navigator_agent, drag_drop_agent, formatter_agent],
    model=model,
    prompt='''You are the head teacher managing Scratch coding helpers for children.

    WORKFLOW RULES:
    
    1. For "how to make/create" questions → code_helper_agent
       - Get category and block info
       - Pass position data to formatter
    
    2. For "is my code correct" questions → code_checker_agent  
       - Check workspace blocks
       - Pass findings with positions to formatter
    
    3. For "click/go to/open" requests → navigator_agent
       - Handle UI navigation
       - No need for formatter unless explaining
    
    4. For "drag/move block" requests → drag_drop_agent
       - Get positions from other agents if needed
       - Execute drag operation
    
    5. ALWAYS end with formatter_agent for child-facing responses
       - Exception: Simple navigation confirmations
    
    IMPORTANT:
    - Keep agent chains short (max 3 agents)
    - Pass position data between agents
    - Don't ask unnecessary questions
    - Be decisive - pick the right agent immediately
    
    Example flows:
    - "How do I make my sprite jump?" → code_helper → formatter
    - "Is my code right?" → code_checker → formatter  
    - "Click on Motion" → navigator (done)
    - "Drag move block to workspace" → drag_drop (done)'''
)


def create_scratch_assistant():
    """Create and initialize the Scratch assistant."""
    return supervisor.compile()

def process_user_input(app, user_input: str, chat_history: List = None):
    """Process user input and return response."""
    if chat_history is None:
        chat_history = []
    
    # Add context about current workspace state
    workspace_state = get_workspace_blocks()
    context = f"Current workspace: {workspace_state['message']}\n\nUser question: {user_input}"
    
    result = app.invoke({
        "messages": chat_history + [{"role": "user", "content": context}]
    })
    
    # Extract the assistant's response
    for m in result["messages"]:
        if m.type == "ai":
            return m.content, result["messages"]
    
    return "I'm not sure how to help with that. Can you try asking in a different way?", result["messages"]


if __name__ == "__main__":
    # Initialize the assistant
    app = create_scratch_assistant()
    chat_history = []
    
    print("🎮 Scratch Coding Assistant Ready!")
    print("Ask me anything about making cool programs in Scratch!\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("👋 See you next time! Keep coding!")
            break
        
        response, chat_history = process_user_input(app, user_input, chat_history)
        print(f"Assistant: {response}\n")