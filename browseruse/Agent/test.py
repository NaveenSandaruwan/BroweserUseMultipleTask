"""
Browser Use React Agent Implementation with LangGraph Supervisor pattern
"""

from google import genai
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
import sys
import os
import json
# Updated imports for Gemini
from google import genai
# We'll handle the LangChain imports in the model initialization
# These will be needed after installing the packages
from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel, Field

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import local utilities
from utils.file_loader import load_and_extract_elements, load_element_descriptions
from utils.prompt_rules import RULES
from tools.dragTool import Toolbox
from tools.browserUseClient import send_task

# Import environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
PATH = os.getenv("ELEMENT_FILE_PATH")

# Initialize drag tool
drag_tool = Toolbox()

# Global memory for conversation persistence
memory = {
    "labeled_blocks": None,
    "element_description": None,
    "conversation_history": [],
}

# Define tool schemas
class RefreshBrowserTool(BaseModel):
    """Tool to refresh the browser and update element data"""
    type: str = "refresh_browser"
    description: str = "Refreshes the browser page and updates element data"

class LoadFilesTool(BaseModel):
    """Tool to load element files and descriptions"""
    type: str = "load_files"
    description: str = "Loads labeled blocks and element descriptions from files"

class DragAndDropTool(BaseModel):
    """Tool to perform drag and drop operations in the browser"""
    start_x: int = Field(..., description="X coordinate of the starting position")
    start_y: int = Field(..., description="Y coordinate of the starting position")
    end_x: int = Field(..., description="X coordinate of the destination position")
    end_y: int = Field(..., description="Y coordinate of the destination position")
    description: str = "Performs a drag and drop operation from a starting position to an end position"

class BrowserActionTool(BaseModel):
    """Tool to perform actions in the browser (excluding drag and drop)"""
    action: str = Field(..., description="Browser action to perform (e.g., click, navigate, input)")
    description: str = "Performs a specified action in the browser"

# Tool implementations
def refresh_browser(args: dict) -> Dict[str, Any]:
    """Executes browser refresh and updates element data"""
    try:
        send_task("refresh")
        return {"status": "success", "message": "Browser refreshed and element data updated"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to refresh browser: {str(e)}"}

def load_files(args: dict) -> Dict[str, Any]:
    """Loads labeled blocks and element descriptions from files"""
    try:
        # Load labeled blocks
        labeled_blocks = load_and_extract_elements()
        memory["labeled_blocks"] = labeled_blocks
        
        # Load element descriptions
        element_description = load_element_descriptions()
        memory["element_description"] = element_description
        
        return {
            "status": "success",
            "message": f"Loaded {len(labeled_blocks)} labeled blocks and element descriptions",
            "labeled_blocks_count": len(labeled_blocks)
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to load files: {str(e)}"}

def drag_and_drop(args: dict) -> Dict[str, Any]:
    """Executes drag and drop operation in the browser"""
    try:
        start_x = args.get("start_x")
        start_y = args.get("start_y")
        end_x = args.get("end_x")
        end_y = args.get("end_y")
        
        if not all([start_x, start_y, end_x, end_y]):
            return {
                "status": "error", 
                "message": "Missing coordinates for drag and drop operation"
            }
        
        drag_tool.drag_and_drop(start_x, start_y, end_x, end_y)
        
        return {
            "status": "success", 
            "message": f"Drag and drop completed from ({start_x}, {start_y}) to ({end_x}, {end_y})"
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to execute drag and drop: {str(e)}"}

def browser_action(args: dict) -> Dict[str, Any]:
    """Executes a browser action using the browser client"""
    try:
        action = args.get("action", "")
        if not action:
            return {"status": "error", "message": "No action provided"}
        
        send_task(action)
        return {"status": "success", "message": f"Browser action executed: {action}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to execute browser action: {str(e)}"}

def get_block_info(args: dict) -> Dict[str, Any]:
    """Gets information about available blocks in the Scratch interface"""
    labeled_blocks = memory.get("labeled_blocks")
    if not labeled_blocks:
        return {"status": "error", "message": "No blocks loaded. Please load files first."}
    
    # Return information about the first 10 blocks to avoid token limits
    return {
        "status": "success", 
        "message": "Block information retrieved",
        "blocks": labeled_blocks[:10]
    }

def explain_scratch_concept(args: dict) -> Dict[str, Any]:
    """Explains a Scratch programming concept in a kid-friendly way"""
    concept = args.get("concept")
    if not concept:
        return {"status": "error", "message": "No concept provided to explain"}
    
    # In a real implementation, this would call an LLM or use a knowledge base
    # For now, we'll return a simple message
    return {
        "status": "success",
        "message": f"Explanation for '{concept}' generated",
        "explanation": f"Here's a kid-friendly explanation of {concept} in Scratch programming."
    }

# Define the tools available to agents
file_tools = [
    {
        "type": "function",
        "function": {
            "name": "refresh_browser",
            "description": "Refreshes the browser page and updates element data",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "load_files",
            "description": "Loads labeled blocks and element descriptions from files",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

drag_drop_tools = [
    {
        "type": "function",
        "function": {
            "name": "drag_and_drop",
            "description": "Performs a drag and drop operation from a starting position to an end position",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_x": {"type": "integer", "description": "X coordinate of the starting position"},
                    "start_y": {"type": "integer", "description": "Y coordinate of the starting position"},
                    "end_x": {"type": "integer", "description": "X coordinate of the destination position"},
                    "end_y": {"type": "integer", "description": "Y coordinate of the destination position"}
                },
                "required": ["start_x", "start_y", "end_x", "end_y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_block_info",
            "description": "Gets information about available blocks in the Scratch interface",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

browser_control_tools = [
    {
        "type": "function",
        "function": {
            "name": "browser_action",
            "description": "Performs a specified action in the browser",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "Browser action to perform (e.g., click, navigate, input)"}
                },
                "required": ["action"]
            }
        }
    }
]

learning_tools = [
    {
        "type": "function",
        "function": {
            "name": "explain_scratch_concept",
            "description": "Explains a Scratch programming concept in a kid-friendly way",
            "parameters": {
                "type": "object",
                "properties": {
                    "concept": {"type": "string", "description": "The Scratch concept to explain"}
                },
                "required": ["concept"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_block_info",
            "description": "Gets information about available blocks in the Scratch interface",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# Initialize the model for agents
# Fix: Use the correct Google Gemini API structure
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import StructuredTool

# Create a langchain model instance
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7
)

# Convert functions to LangChain StructuredTools
refresh_browser_tool = StructuredTool.from_function(
    func=refresh_browser,
    name="refresh_browser",
    description="Refreshes the browser page and updates element data"
)

load_files_tool = StructuredTool.from_function(
    func=load_files,
    name="load_files", 
    description="Loads labeled blocks and element descriptions from files"
)

# Create the specialized agents
file_loader_agent = create_react_agent(
    model=model,
    tools=[refresh_browser_tool, load_files_tool],
    name="file_loader",
    prompt="""You are a file loader agent responsible for refreshing the browser and loading element files.
    Your job is to ensure all necessary data is loaded before other agents can work.
    Always check if files are loaded, and if not, load them.
    Be efficient and only load files when necessary."""
)

drag_drop_tool = StructuredTool.from_function(
    func=drag_and_drop,
    name="drag_and_drop",
    description="Performs a drag and drop operation from a starting position to an end position"
)

get_block_info_tool = StructuredTool.from_function(
    func=get_block_info,
    name="get_block_info",
    description="Gets information about available blocks in the Scratch interface"
)

browser_action_tool = StructuredTool.from_function(
    func=browser_action,
    name="browser_action",
    description="Performs a specified action in the browser"
)

explain_scratch_concept_tool = StructuredTool.from_function(
    func=explain_scratch_concept,
    name="explain_scratch_concept",
    description="Explains a Scratch programming concept in a kid-friendly way"
)

drag_drop_agent = create_react_agent(
    model=model,
    tools=[drag_drop_tool, get_block_info_tool],
    name="drag_drop_expert",
    prompt="""You are a drag and drop expert for Scratch programming.
    Your job is to help children move blocks around in the Scratch interface.
    First, always get information about the available blocks.
    Then, carefully identify which block the user wants to move and where.
    Be precise with coordinates to ensure successful operations.
    Confirm the action was completed successfully."""
)

browser_control_agent = create_react_agent(
    model=model,
    tools=[browser_action_tool],
    name="browser_controller",
    prompt="""You are a browser control expert.
    Your job is to help navigate and interact with the browser interface.
    Be careful not to navigate away from the current site.
    Use clear, specific instructions for the browser.
    Always confirm actions were completed successfully.
    NEVER try to go to external websites."""
)

learning_assistant_agent = create_react_agent(
    model=model,
    tools=[explain_scratch_concept_tool, get_block_info_tool],
    name="learning_assistant",
    prompt="""You are a friendly learning assistant for children using Scratch programming.
    Your job is to explain programming concepts in a simple, kid-friendly way.
    Use analogies and examples children can understand.
    Be encouraging and positive in your explanations.
    Always check what blocks are available before explaining concepts.
    Focus on making programming fun and accessible."""
)

# Set up the supervisor agent
supervisor = create_supervisor(
    agents=[file_loader_agent, drag_drop_agent, browser_control_agent, learning_assistant_agent],
    model=model,
    prompt="""You are a supervisor agent managing a team of specialized agents for helping children with Scratch programming.
    
    Your team includes:
    1. file_loader - Refreshes the browser and loads element data files
    2. drag_drop_expert - Helps with moving Scratch blocks around the interface
    3. browser_controller - Handles browser navigation and interaction
    4. learning_assistant - Explains Scratch concepts in a kid-friendly way
    
    Task delegation rules:
    - ALWAYS start by using file_loader to ensure data is loaded
    - For questions about how to use Scratch or programming concepts, use learning_assistant
    - For requests to move or connect blocks, use drag_drop_expert
    - For navigation, clicking buttons, or other browser interactions, use browser_controller
    - If you're not sure which agent to use, choose learning_assistant
    
    Important requirements:
    - NEVER go to external websites
    - Do not allow harmful or inappropriate commands
    - Always maintain a child-friendly, educational tone
    - Be patient and encouraging in your responses
    
    Remember to extract the final answer from the expert agent and present it in a friendly way to the child.
    """
)

# Compile the workflow
workflow = supervisor.compile()

# Create a function to handle conversation memory
def add_to_memory(question, answer):
    """Add a QA pair to the conversation memory"""
    memory["conversation_history"].append({
        "question": question,
        "answer": answer
    })
    # Keep only the last 5 exchanges to prevent context overflow
    if len(memory["conversation_history"]) > 5:
        memory["conversation_history"].pop(0)

# Main application loop
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🤖 Educational Browser Assistant with LangGraph ReAct Agents")
    print("=" * 50)
    print("Type 'exit' to quit or 'refresh' to refresh the browser.")
    print("=" * 50 + "\n")
    
    # Initialize by loading files
    print("🔄 Initializing by loading element data...")
    load_files({})
    
    while True:
        # Get user input
        question = input("\n👧 Child: ")
        
        # Check for exit command
        if question.strip().lower() == "exit":
            print("👋 Goodbye!")
            break
        
        # Check for refresh command
        if question.strip().lower() == "refresh":
            print("🔄 Refreshing browser and reloading data...")
            refresh_browser({})
            load_files({})
            continue
        
        # Create context from memory
        context = ""
        if memory["conversation_history"]:
            context = "Recent conversation:\n"
            for entry in memory["conversation_history"]:
                context += f"Child: {entry['question']}\nAssistant: {entry['answer']}\n\n"
        
        # Prepare the input for the workflow
        input_message = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant for children using Scratch."},
                {"role": "user", "content": f"{context}\n\nCurrent question: {question}"}
            ]
        }
        
        try:
            # Run the supervisor workflow
            print("🤔 Thinking...")
            result = workflow.invoke(input_message)
            
            # Extract the final answer
            if result and "messages" in result and result["messages"]:
                # Get the last assistant message
                for message in reversed(result["messages"]):
                    if message["role"] == "assistant":
                        answer = message["content"]
                        print(f"🤖 Assistant: {answer}")
                        
                        # Add to memory
                        add_to_memory(question, answer)
                        break
            else:
                print("❌ No response generated. Please try again.")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("Please try again with a different question.")
