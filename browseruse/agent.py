import os
import json
import time
import glob
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.pfrebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain.tools import BaseTool
from langchain.schema import BaseMessage
from pydantic import BaseModel, Field

# Browser control imports
import pychrome
import google.generativeai as genai

# Load environment variables
load_dotenv()

@dataclass
class ScratchElement:
    """Represents a Scratch block or element"""
    id: str
    tag: str
    text: str
    visible: bool
    x: float
    y: float
    block_type: Optional[str] = None
    is_child_block: bool = False

class ScratchDOMAnalyzer:
    """Analyzes Scratch DOM and converts to LLM-friendly format"""
    
    def __init__(self, element_file_path: str):
        self.element_file_path = element_file_path
        self.elements: List[ScratchElement] = []
        
    def get_latest_elements_file(self) -> str:
        """Get the most recent elements JSON file"""
        list_of_files = glob.glob(self.element_file_path)
        if not list_of_files:
            raise FileNotFoundError("No JSON files found in the specified path")
        return max(list_of_files, key=os.path.getctime)
    
    def load_elements(self) -> List[ScratchElement]:
        """Load and parse elements from JSON file"""
        latest_file = self.get_latest_elements_file()
        
        with open(latest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        elements = []
        for key in sorted(data.keys(), key=lambda k: int(k)):
            el = data[key]
            bounding_box = el.get("bounding_box", {})
            
            element = ScratchElement(
                id=key,
                tag=el.get("tag_name", ""),
                text=el.get("text_content", ""),
                visible=el.get("is_visible", False),
                x=bounding_box.get("x", 0),
                y=bounding_box.get("y", 0),
                is_child_block=bounding_box.get("x", 0) > 310  # Child blocks have x > 310
            )
            elements.append(element)
        
        self.elements = elements
        return elements
    
    def get_elements_text(self) -> str:
        """Convert elements to text format for LLM"""
        if not self.elements:
            self.load_elements()
            
        element_text = "\n".join([
            f"{e.id}: tag={e.tag}, text={e.text}, visible={e.visible}, "
            f"x={round(e.x) if e.x else e.x}, y={round(e.y) if e.y else e.y}"
            for e in self.elements
        ])
        return element_text

class ScratchBrowserController:
    """Controls browser interactions with Scratch"""
    
    def __init__(self, debug_port: int = 9222):
        self.debug_port = debug_port
        self.browser = None
        self.tab = None
        
    def connect(self):
        """Connect to Chrome browser"""
        try:
            self.browser = pychrome.Browser(url=f"http://127.0.0.1:{self.debug_port}")
            self.tab = self.browser.list_tab()[0]
            self.tab.start()
            print("✅ Connected to Chrome browser")
        except Exception as e:
            print(f"❌ Failed to connect to browser: {e}")
            raise
    
    def drag_and_drop(self, x_start: float, y_start: float, 
                     x_end: float, y_end: float, steps: int = 10, delay: float = 0.05):
        """Perform drag and drop operation"""
        if not self.tab:
            raise RuntimeError("Browser not connected. Call connect() first.")
        
        # Move to starting position
        self.tab.Input.dispatchMouseEvent(type="mouseMoved", x=x_start, y=y_start)
        time.sleep(delay)
        
        # Press mouse down
        self.tab.Input.dispatchMouseEvent(type="mousePressed", x=x_start, y=y_start, 
                                        button="left", clickCount=1)
        time.sleep(delay)
        
        # Move to destination in steps
        for i in range(1, steps + 1):
            x = x_start + (x_end - x_start) * i / steps
            y = y_start + (y_end - y_start) * i / steps
            self.tab.Input.dispatchMouseEvent(type="mouseMoved", x=x, y=y, buttons=1)
            time.sleep(delay)
        
        # Release mouse
        self.tab.Input.dispatchMouseEvent(type="mouseReleased", x=x_end, y=y_end, 
                                        button="left", clickCount=1)
        time.sleep(delay)
        print(f"✅ Drag and drop completed: ({x_start}, {y_start}) → ({x_end}, {y_end})")
    
    def click_element(self, x: float, y: float):
        """Click on an element at specified coordinates"""
        if not self.tab:
            raise RuntimeError("Browser not connected. Call connect() first.")
        
        self.tab.Input.dispatchMouseEvent(type="mousePressed", x=x, y=y, 
                                        button="left", clickCount=1)
        time.sleep(0.1)
        self.tab.Input.dispatchMouseEvent(type="mouseReleased", x=x, y=y, 
                                        button="left", clickCount=1)
        print(f"✅ Clicked at ({x}, {y})")

# Define Tools for LangChain Agents

class ScratchElementAnalysisTool(BaseTool):
    """Tool for analyzing Scratch elements"""
    name = "scratch_element_analyzer"
    description = "Analyzes Scratch blocks and elements on the page"
    
    def __init__(self, dom_analyzer: ScratchDOMAnalyzer):
        super().__init__()
        self.dom_analyzer = dom_analyzer
    
    def _run(self, query: str) -> str:
        """Analyze elements and return information"""
        try:
            elements = self.dom_analyzer.load_elements()
            element_text = self.dom_analyzer.get_elements_text()
            
            # Load block reference
            try:
                with open("browseruse/allElement.txt", "r") as f:
                    block_reference = f.read()
            except FileNotFoundError:
                block_reference = "Block reference file not found"
            
            return f"Current Scratch Elements:\n{element_text}\n\nBlock Reference:\n{block_reference}"
        except Exception as e:
            return f"Error analyzing elements: {e}"

class ScratchBlockFinderTool(BaseTool):
    """Tool for finding specific Scratch blocks"""
    name = "scratch_block_finder"
    description = "Finds specific Scratch blocks by name or functionality"
    
    def __init__(self, dom_analyzer: ScratchDOMAnalyzer):
        super().__init__()
        self.dom_analyzer = dom_analyzer
    
    def _run(self, block_name: str) -> str:
        """Find blocks matching the specified name or functionality"""
        try:
            if not self.dom_analyzer.elements:
                self.dom_analyzer.load_elements()
            
            matching_blocks = []
            for element in self.dom_analyzer.elements:
                if block_name.lower() in element.text.lower() and element.visible:
                    matching_blocks.append(element)
            
            if matching_blocks:
                result = f"Found {len(matching_blocks)} matching blocks:\n"
                for i, block in enumerate(matching_blocks, 1):
                    result += f"{i}. Block ID {block.id}: '{block.text}' at ({block.x}, {block.y})\n"
                return result
            else:
                return f"No visible blocks found matching '{block_name}'"
        except Exception as e:
            return f"Error finding blocks: {e}"

class ScratchControlTool(BaseTool):
    """Tool for controlling Scratch elements (drag, drop, click)"""
    name = "scratch_controller"
    description = "Controls Scratch blocks - can drag, drop, and click elements"
    
    def __init__(self, browser_controller: ScratchBrowserController, dom_analyzer: ScratchDOMAnalyzer):
        super().__init__()
        self.browser_controller = browser_controller
        self.dom_analyzer = dom_analyzer
    
    def _run(self, action: str) -> str:
        """Execute browser control actions"""
        try:
            if not self.browser_controller.tab:
                self.browser_controller.connect()
            
            # Parse action (format: "drag:id1:id2" or "click:id" or "drag:x1,y1:x2,y2")
            parts = action.split(":")
            
            if parts[0] == "drag" and len(parts) == 3:
                source = parts[1]
                target = parts[2]
                
                # Check if coordinates or element IDs
                if "," in source and "," in target:
                    # Direct coordinates
                    x1, y1 = map(float, source.split(","))
                    x2, y2 = map(float, target.split(","))
                else:
                    # Element IDs - find coordinates
                    if not self.dom_analyzer.elements:
                        self.dom_analyzer.load_elements()
                    
                    source_elem = next((e for e in self.dom_analyzer.elements if e.id == source), None)
                    target_elem = next((e for e in self.dom_analyzer.elements if e.id == target), None)
                    
                    if not source_elem or not target_elem:
                        return f"Could not find elements with IDs {source} or {target}"
                    
                    x1, y1 = source_elem.x, source_elem.y
                    x2, y2 = target_elem.x, target_elem.y
                
                self.browser_controller.drag_and_drop(x1, y1, x2, y2)
                return f"Successfully dragged from ({x1}, {y1}) to ({x2}, {y2})"
            
            elif parts[0] == "click" and len(parts) == 2:
                target = parts[1]
                
                if "," in target:
                    # Direct coordinates
                    x, y = map(float, target.split(","))
                else:
                    # Element ID
                    if not self.dom_analyzer.elements:
                        self.dom_analyzer.load_elements()
                    
                    target_elem = next((e for e in self.dom_analyzer.elements if e.id == target), None)
                    if not target_elem:
                        return f"Could not find element with ID {target}"
                    
                    x, y = target_elem.x, target_elem.y
                
                self.browser_controller.click_element(x, y)
                return f"Successfully clicked at ({x}, {y})"
            
            else:
                return "Invalid action format. Use 'drag:source:target' or 'click:target'"
                
        except Exception as e:
            return f"Error executing action: {e}"

class ScratchTutorAgent:
    """Main agent system for Scratch tutoring"""
    
    def __init__(self):
        # Initialize components
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        element_path = os.getenv("ELEMENT_FILE_PATH", "*.json")
        self.dom_analyzer = ScratchDOMAnalyzer(element_path)
        self.browser_controller = ScratchBrowserController()
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=self.api_key,
            temperature=0.3
        )
        
        # Create tools
        self.element_analyzer = ScratchElementAnalysisTool(self.dom_analyzer)
        self.block_finder = ScratchBlockFinderTool(self.dom_analyzer)
        self.controller = ScratchControlTool(self.browser_controller, self.dom_analyzer)
        
        # Create specialized agents
        self.analysis_agent = create_react_agent(
            model=self.llm,
            tools=[self.element_analyzer, self.block_finder],
            name='scratch_analyzer',
            prompt='''You are a Scratch programming expert who analyzes Scratch blocks and workspace.
            Your job is to:
            1. Understand the current state of the Scratch workspace
            2. Identify available blocks and their positions
            3. Explain what blocks do and how they work together
            4. Help users understand Scratch programming concepts
            Always use the tools to get current information about the workspace.'''
        )
        
        self.control_agent = create_react_agent(
            model=self.llm,
            tools=[self.controller, self.block_finder],
            name='scratch_controller',
            prompt='''You are a Scratch automation expert who can control the Scratch interface.
            Your job is to:
            1. Find specific blocks on the workspace
            2. Drag and drop blocks to create programs
            3. Click on elements to interact with them
            4. Execute user instructions for building Scratch programs
            Always find block positions first before attempting to control them.'''
        )
        
        self.tutor_agent = create_react_agent(
            model=self.llm,
            tools=[self.element_analyzer, self.block_finder],
            name='scratch_tutor',
            prompt='''You are an expert Scratch programming tutor.
            Your job is to:
            1. Answer questions about Scratch programming concepts
            2. Explain how different blocks work
            3. Suggest programming solutions
            4. Guide users through creating programs step-by-step
            5. Provide educational explanations suitable for beginners
            Be encouraging, patient, and educational in your responses.'''
        )
        
        # Create supervisor
        self.workflow = create_supervisor(
            [self.analysis_agent, self.control_agent, self.tutor_agent],
            model=self.llm,
            prompt='''You are supervising a team of Scratch programming experts.
            
            Route tasks as follows:
            - For analyzing current workspace, finding blocks, or understanding what's on screen: use scratch_analyzer
            - For controlling the interface, dragging blocks, or automating actions: use scratch_controller  
            - For explaining concepts, answering questions, or providing tutorials: use scratch_tutor
            
            The user is working with a Scratch programming environment. Help them learn, understand, and create programs.'''
        )
        
        self.chat_app = self.workflow.compile()
        self.chat_history = []
    
    async def process_query(self, user_input: str) -> str:
        """Process user query and return response"""
        try:
            result = self.chat_app.invoke({
                "messages": self.chat_history + [{"role": "user", "content": user_input}]
            })
            
            # Update chat history
            self.chat_history.extend(result["messages"])
            
            # Extract AI response
            for message in result["messages"]:
                if hasattr(message, 'type') and message.type == "ai":
                    return message.content
                elif isinstance(message, dict) and message.get("role") == "assistant":
                    return message.get("content", "")
            
            return "I processed your request, but couldn't generate a response."
            
        except Exception as e:
            return f"Error processing query: {e}"
    
    def run_interactive(self):
        """Run interactive chat loop"""
        print("🎯 Scratch Extension Agent Started!")
        print("Ask me about Scratch blocks, request actions, or get programming help.")
        print("Type 'exit' to quit.\n")
        
        try:
            # Connect to browser
            self.browser_controller.connect()
        except Exception as e:
            print(f"⚠️  Browser connection failed: {e}")
            print("Some features may not work without browser connection.\n")
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("🤖 Agent: ", end="")
                response = asyncio.run(self.process_query(user_input))
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

# Example usage
if __name__ == "__main__":
    try:
        agent = ScratchTutorAgent()
        agent.run_interactive()
    except Exception as e:
        print(f"Failed to start agent: {e}")