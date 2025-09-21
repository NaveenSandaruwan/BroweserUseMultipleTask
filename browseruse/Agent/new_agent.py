from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import BaseTool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import os
import sys
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Add your existing imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

load_dotenv()

try:
    from utils.file_loader import load_and_extract_elements, load_scratch_descriptions
    from tools.browserUseClient import send_task
    from tools.dragTool import Toolbox
except ImportError as e:
    print(f"Warning: Could not import some tools: {e}")
    # Create fallback functions
    def load_and_extract_elements():
        return []
    def load_scratch_descriptions():
        return "No descriptions available"
    def send_task(task):
        return f"Would execute: {task}"
    class Toolbox:
        def drag_and_drop(self, x1, y1, x2, y2):
            return f"Would drag from ({x1},{y1}) to ({x2},{y2})"

# Initialize LLM
GEMINIAPI = os.getenv("GOOGLE_API_KEY")
if not GEMINIAPI:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GEMINIAPI,
    temperature=0.3
)

class ScratchPageAnalysisTool(BaseTool):
    """Comprehensive tool for analyzing the Scratch page"""
    name: str = "analyze_scratch_page"
    description: str = "Analyze the current Scratch page and get information about elements, blocks, and layout"
    
    def _run(self, query: str = "overview") -> str:
        """Analyze the Scratch page"""
        try:
            result = {
                "status": "success",
                "timestamp": "current",
                "page_elements": {},
                "analysis": {}
            }
            
            # Get elements from JSON file
            elements_path = os.getenv("ELEMENT_FILE_PATH")
            if elements_path and os.path.exists(elements_path):
                try:
                    with open(elements_path, 'r', encoding='utf-8') as f:
                        elements_data = json.load(f)
                    
                    # Process elements
                    scratch_blocks = []
                    ui_elements = []
                    workspace_elements = []
                    
                    for element_id, element_info in elements_data.items():
                        text_content = element_info.get('text_content', '')
                        bounding_box = element_info.get('bounding_box', {})
                        
                        element = {
                            "id": element_id,
                            "text": text_content,
                            "tag": element_info.get('tag_name', ''),
                            "visible": element_info.get('is_visible', False),
                            "x": bounding_box.get('x'),
                            "y": bounding_box.get('y'),
                            "width": bounding_box.get('width'),
                            "height": bounding_box.get('height')
                        }
                        
                        if text_content and element["visible"]:
                            # Categorize elements
                            text_lower = text_content.lower()
                            x_pos = element["x"] or 0
                            
                            if any(keyword in text_lower for keyword in ['move', 'turn', 'steps', 'degrees', 'glide', 'go to']):
                                scratch_blocks.append(element)
                            elif x_pos > 310:  # Workspace area
                                workspace_elements.append(element)
                            elif any(keyword in text_lower for keyword in ['file', 'edit', 'sprite', 'costume', 'sound']):
                                ui_elements.append(element)
                    
                    result["page_elements"] = {
                        "scratch_blocks": scratch_blocks[:10],  # Limit for readability
                        "workspace_elements": workspace_elements,
                        "ui_elements": ui_elements[:10],
                        "total_elements": len(elements_data),
                        "visible_elements": len([e for e in elements_data.values() if e.get('is_visible', False)])
                    }
                    
                    result["analysis"] = {
                        "has_scratch_blocks": len(scratch_blocks) > 0,
                        "has_workspace_code": len(workspace_elements) > 0,
                        "workspace_block_count": len(workspace_elements),
                        "available_block_count": len(scratch_blocks)
                    }
                    
                except Exception as file_error:
                    result["error"] = f"Error reading elements file: {file_error}"
            else:
                result["error"] = "Elements file not found or path not set"
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": "Failed to analyze Scratch page"
            })

class ElementSearchTool(BaseTool):
    """Tool for finding specific elements by text or properties"""
    name: str = "search_elements"
    description: str = "Search for specific elements on the page by text content, position, or properties"
    
    def _run(self, search_query: str) -> str:
        """Search for elements matching the query"""
        try:
            elements_path = os.getenv("ELEMENT_FILE_PATH")
            if not elements_path or not os.path.exists(elements_path):
                return json.dumps({"error": "Elements file not found"})
            
            with open(elements_path, 'r', encoding='utf-8') as f:
                elements_data = json.load(f)
            
            matching_elements = []
            search_lower = search_query.lower()
            
            for element_id, element_info in elements_data.items():
                text_content = element_info.get('text_content', '')
                tag_name = element_info.get('tag_name', '')
                
                # Check if element matches search query
                if (text_content and search_lower in text_content.lower()) or \
                   (tag_name and search_lower in tag_name.lower()) or \
                   search_lower in element_id.lower():
                    
                    bounding_box = element_info.get('bounding_box', {})
                    matching_elements.append({
                        "element_id": element_id,
                        "text_content": text_content,
                        "tag_name": tag_name,
                        "is_visible": element_info.get('is_visible', False),
                        "position": {
                            "x": bounding_box.get('x'),
                            "y": bounding_box.get('y'),
                            "width": bounding_box.get('width'),
                            "height": bounding_box.get('height')
                        }
                    })
            
            result = {
                "query": search_query,
                "matches_found": len(matching_elements),
                "elements": matching_elements[:20]  # Limit results
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"Search failed: {e}"})

class WebNavigationTool(BaseTool):
    """Tool for web navigation and interaction"""
    name: str = "navigate_webpage"
    description: str = "Navigate the webpage, click buttons, and interact with interface elements"
    
    def _run(self, action: str) -> str:
        """Execute web navigation action"""
        try:
            result = send_task(action)
            return json.dumps({
                "action": action,
                "result": str(result),
                "status": "completed"
            })
        except Exception as e:
            return json.dumps({
                "action": action,
                "error": str(e),
                "status": "failed"
            })

class DragDropTool(BaseTool):
    """Tool for drag and drop operations"""
    name: str = "drag_drop_blocks"
    description: str = "Perform drag and drop operations to move blocks around the Scratch interface"
    
    def __init__(self):
        super().__init__()
        self.toolbox = Toolbox()
    
    def _run(self, operation: str) -> str:
        """Perform drag and drop operation"""
        try:
            # Parse operation format: "source_x,source_y:target_x,target_y"
            if ':' not in operation:
                return json.dumps({"error": "Invalid format. Use 'source_x,source_y:target_x,target_y'"})
            
            source_part, target_part = operation.split(':')
            
            # Parse coordinates
            source_coords = [float(x.strip()) for x in source_part.split(',')]
            target_coords = [float(x.strip()) for x in target_part.split(',')]
            
            if len(source_coords) != 2 or len(target_coords) != 2:
                return json.dumps({"error": "Invalid coordinates format"})
            
            source_x, source_y = source_coords
            target_x, target_y = target_coords
            
            # Perform drag operation
            self.toolbox.drag_and_drop(source_x, source_y, target_x, target_y)
            
            return json.dumps({
                "operation": "drag_drop",
                "source": {"x": source_x, "y": source_y},
                "target": {"x": target_x, "y": target_y},
                "status": "completed"
            })
            
        except Exception as e:
            return json.dumps({
                "operation": "drag_drop",
                "error": str(e),
                "status": "failed"
            })


def create_scratch_react_agent(agent_type: str, tools: List[BaseTool]) -> AgentExecutor:
    """Create a React agent with proper prompt template"""
    
    # Define agent-specific prompts
    prompts = {
        "page_analyzer": """You are a Scratch page analysis expert. Your job is to analyze the current Scratch programming interface and provide clear information about what's visible.

Available tools: {tools}
Tool names: {tool_names}

When analyzing the page:
1. Use the analyze_scratch_page tool to get current page state
2. Organize information clearly for the user
3. Focus on blocks, workspace content, and interface elements
4. Always mention specific coordinates when describing elements

Use this format:
Question: {input}
Thought: I need to analyze what's currently on the Scratch page
Action: analyze_scratch_page
Action Input: overview
Observation: [tool result]
Thought: I now understand what's on the page
Final Answer: [clear explanation with coordinates]

Question: {input}
{agent_scratchpad}""",

        "element_finder": """You are a Scratch element locator. Your job is to find specific blocks, buttons, or interface elements and provide their exact positions.

Available tools: {tools}
Tool names: {tool_names}

When searching for elements:
1. Use the search_elements tool with the user's search query
2. Provide exact coordinates (x, y) for found elements
3. Describe what each element does
4. Mention if elements are visible and clickable

Use this format:
Question: {input}
Thought: I need to search for specific elements
Action: search_elements  
Action Input: [user's search term]
Observation: [search results]
Thought: I found the elements and their positions
Final Answer: [detailed response with coordinates]

Question: {input}
{agent_scratchpad}""",

        "navigator": """You are a Scratch navigation assistant. Your job is to help users navigate the interface, click buttons, and interact with elements.

Available tools: {tools}
Tool names: {tool_names}

When navigating:
1. Use the navigate_webpage tool to perform actions
2. Be specific about what action you're taking
3. Confirm successful completion
4. Provide feedback on what happened

Use this format:
Question: {input}
Thought: I need to perform a navigation action
Action: navigate_webpage
Action Input: [specific action description]
Observation: [action result]
Thought: The action was completed
Final Answer: [confirmation of what was done]

Question: {input}
{agent_scratchpad}""",

        "block_mover": """You are a Scratch block movement specialist. Your job is to drag and drop blocks within the Scratch interface.

Available tools: {tools}
Tool names: {tool_names}

When moving blocks:
1. First search for the source block's coordinates using search_elements
2. Determine the target location (workspace area is typically around x=400-600)
3. Use drag_drop_blocks with exact coordinates
4. Confirm the movement was successful

Use this format:
Question: {input}
Thought: I need to find the block's current position first
Action: search_elements
Action Input: [block name]
Observation: [block location]
Thought: Now I'll move it to the workspace
Action: drag_drop_blocks
Action Input: source_x,source_y:target_x,target_y
Observation: [drag result]
Thought: The block has been moved
Final Answer: [confirmation with coordinates]

Question: {input}
{agent_scratchpad}"""
    }
    
    prompt_template = PromptTemplate(
        template=prompts.get(agent_type, prompts["page_analyzer"]),
        input_variables=["input", "tools", "tool_names", "agent_scratchpad"]
    )
    
    # Create the React agent
    agent = create_react_agent(model, tools, prompt_template)
    
    # Return AgentExecutor with proper configuration
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
        return_intermediate_steps=True
    )


class ScratchAgentCoordinator:
    """Coordinates multiple React agents for Scratch programming assistance"""
    
    def __init__(self):
        # Initialize tools
        self.page_tool = ScratchPageAnalysisTool()
        self.search_tool = ElementSearchTool()
        self.nav_tool = WebNavigationTool()
        self.drag_tool = DragDropTool()
        
        # Create specialized agents
        self.page_analyzer = create_scratch_react_agent(
            "page_analyzer", 
            [self.page_tool, self.search_tool]
        )
        
        self.element_finder = create_scratch_react_agent(
            "element_finder",
            [self.search_tool, self.page_tool]
        )
        
        self.navigator = create_scratch_react_agent(
            "navigator",
            [self.nav_tool, self.search_tool]
        )
        
        self.block_mover = create_scratch_react_agent(
            "block_mover",
            [self.search_tool, self.drag_tool]
        )
        
        # Conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
    def determine_agent_type(self, user_input: str) -> str:
        """Determine which agent should handle the user input"""
        user_lower = user_input.lower()
        
        # Navigation keywords
        if any(word in user_lower for word in ['go to', 'click', 'navigate', 'open', 'press', 'button']):
            return "navigator"
        
        # Drag/move keywords
        if any(word in user_lower for word in ['drag', 'drop', 'move', 'put', 'place']):
            return "block_mover"
        
        # Search/find keywords
        if any(word in user_lower for word in ['find', 'where is', 'locate', 'search for']):
            return "element_finder"
        
        # Default to page analysis for general questions
        return "page_analyzer"
    
    def process_request(self, user_input: str) -> str:
        """Process user request with appropriate agent"""
        try:
            agent_type = self.determine_agent_type(user_input)
            print(f"DEBUG: Routing to {agent_type} agent")
            
            # Select appropriate agent
            if agent_type == "navigator":
                agent = self.navigator
            elif agent_type == "block_mover":
                agent = self.block_mover
            elif agent_type == "element_finder":
                agent = self.element_finder
            else:
                agent = self.page_analyzer
            
            # Execute with the selected agent
            result = agent.invoke({"input": user_input})
            
            # Extract the output
            if isinstance(result, dict):
                response = result.get("output", str(result))
            else:
                response = str(result)
            
            # Store in memory
            self.memory.save_context(
                {"input": user_input},
                {"output": response}
            )
            
            return response
            
        except Exception as e:
            error_msg = f"I encountered an error while processing your request: {e}"
            print(f"DEBUG: Error in process_request: {e}")
            return error_msg
    
    def run_interactive(self):
        """Run interactive chat session"""
        print("🎮 Welcome to your Scratch Programming Assistant!")
        print("I can help you:")
        print("• Analyze what's on the Scratch page")
        print("• Find specific blocks or elements") 
        print("• Navigate the interface")
        print("• Move blocks around")
        print("\nType 'quit' to exit.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Goodbye! Happy coding with Scratch!")
                    break
                
                if not user_input:
                    continue
                
                print("Assistant: ", end="", flush=True)
                response = self.process_request(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\nGoodbye! Keep exploring Scratch!")
                break
            except Exception as e:
                print(f"An error occurred: {e}")



if __name__ == "__main__":
    try:
        coordinator = ScratchAgentCoordinator()
        coordinator.run_interactive()
    except Exception as e:
        print(f"Failed to start Scratch assistant: {e}")
        print("Please check your environment variables and dependencies.")