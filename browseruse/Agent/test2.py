from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.file_loader import load_and_extract_elements, load_scratch_descriptions
from tools.browserUseClient import send_task
from tools.dragTool import Toolbox
import json



GEMINIAPI = os.getenv("GOOGLE_API_KEY") or "AIzaSyBRYRYAjFStLg_xFoNFTaSsaphNuNkmd_I"
# print("GEMINI_API:", GEMINIAPI)  # Debugging line to check if the API key is loaded correctly
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GEMINIAPI,
    temperature=0.7
)


# Define custom functions to use as tools for our agents
def extract_all_element_text():
    """
    Extract ONLY the text content from all elements in elements.json directly.
    This provides a clear list of all available text on the page.
    
    Returns:
        dict: Dictionary with all text content available on the page
    """
    # Load elements.json directly for full access
    elements_path = r"E:\VS CODE\Agentic AI\BrowserUse\element_data\elements.json"
    try:
        with open(elements_path, 'r', encoding='utf-8') as f:
            elements_data = json.load(f)
    except Exception as e:
        print(f"Error loading elements.json: {e}")
        return {"error": str(e)}
    
    # Extract all text content only
    text_contents = []
    seen_texts = set()
    text_to_element_ids = {}  # Map text content to element IDs
    
    for element_id, element_info in elements_data.items():
        text = element_info.get('text_content')
        if text and text not in seen_texts and len(str(text).strip()) > 0:
            seen_texts.add(text)
            text_contents.append({
                'text': text,
                'element_id': element_id
            })
            # Map this text to its element ID for easy lookup
            if text not in text_to_element_ids:
                text_to_element_ids[text] = []
            text_to_element_ids[text].append(element_id)
    
    # Group by text types
    scratch_blocks = []
    ui_elements = []
    navigation = []
    other_text = []
    
    # Common scratch block text patterns
    scratch_keywords = ['move', 'turn', 'steps', 'degrees', 'glide', 'secs', 'go to']
    
    # Common UI element text patterns
    ui_keywords = ['sprite', 'size', 'direction', 'duplicate', 'export', 'delete']
    
    # Navigation text patterns
    nav_keywords = ['file', 'edit', 'settings', 'code', 'costumes', 'sounds', 'join']
    
    for item in text_contents:
        text = item['text'].lower()
        categorized = False
        
        # Check for scratch blocks
        for keyword in scratch_keywords:
            if keyword in text:
                scratch_blocks.append(item)
                categorized = True
                break
                
        if not categorized:
            # Check for UI elements
            for keyword in ui_keywords:
                if keyword in text:
                    ui_elements.append(item)
                    categorized = True
                    break
        
        if not categorized:
            # Check for navigation
            for keyword in nav_keywords:
                if keyword in text:
                    navigation.append(item)
                    categorized = True
                    break
        
        if not categorized:
            other_text.append(item)
    
    return {
        "all_text_elements": text_contents,
        "total_text_elements": len(text_contents),
        "text_to_element_ids": text_to_element_ids,
        "categorized_elements": {
            "scratch_blocks": scratch_blocks,
            "ui_elements": ui_elements,
            "navigation": navigation,
            "other_text": other_text
        },
        "scratch_block_count": len(scratch_blocks),
        "ui_element_count": len(ui_elements),
        "navigation_count": len(navigation),
        "other_text_count": len(other_text),
        "page_overview": "The following text content is available on the page"
    }

def get_element_by_text_content(text_query: str):
    """
    Retrieve FULL element details directly from elements.json based on matching text content.
    This function focuses on providing complete position information for elements with matching text.
    
    Args:
        text_query (str): The text content to search for in elements
        
    Returns:
        dict: Complete element details including all position data
    """
    # Load elements.json directly for full access to all position data
    elements_path = r"E:\VS CODE\Agentic AI\BrowserUse\element_data\elements.json"
    try:
        with open(elements_path, 'r', encoding='utf-8') as f:
            elements_data = json.load(f)
    except Exception as e:
        print(f"Error loading elements.json: {e}")
        return {"error": str(e)}
    
    # Find elements with matching text content
    matched_elements = []
    for element_id, element_info in elements_data.items():
        text_content = element_info.get('text_content', '')
        if text_content and text_query.lower() in str(text_content).lower():
            # Get full position details from the bounding box
            position_details = element_info.get('bounding_box', {})
            
            # Create a complete element record with emphasis on position data
            element_record = {
                'element_id': element_id,
                'text_content': text_content,
                'tag_name': element_info.get('tag_name', ''),
                'is_visible': element_info.get('is_visible', False),
                'position': {
                    'x': position_details.get('x'),
                    'y': position_details.get('y'),
                    'width': position_details.get('width'),
                    'height': position_details.get('height'),
                    'top': position_details.get('top'),
                    'left': position_details.get('left'),
                    'bottom': position_details.get('bottom'),
                    'right': position_details.get('right')
                },
                'position_description': f"Located at coordinates ({position_details.get('x', 'unknown')}, {position_details.get('y', 'unknown')})",
                'center_point': {
                    'x': position_details.get('x', 0) + (position_details.get('width', 0) / 2 if position_details.get('width') else 0),
                    'y': position_details.get('y', 0) + (position_details.get('height', 0) / 2 if position_details.get('height') else 0)
                }
            }
            matched_elements.append(element_record)
    
    # Also get descriptions related to the text query
    scratch_descriptions = load_scratch_descriptions()
    relevant_descriptions = []
    for line in scratch_descriptions.split('\n'):
        if text_query.lower() in line.lower():
            relevant_descriptions.append(line.strip())
    
    return {
        "matched_elements": matched_elements,
        "total_matches": len(matched_elements),
        "query": text_query,
        "has_position_data": any(e['position']['x'] is not None for e in matched_elements),
        "descriptions": relevant_descriptions[:10],
        "position_data": "Complete position data from elements.json is included for all matched elements"
    }


def get_relevant_content(query: str):
    """
    Retrieve content relevant to a user query from the website elements and Scratch descriptions.
    
    Args:
        query (str): The user's query or search term
        
    Returns:
        dict: Dictionary with relevant content
    """
    # First, get element details by text content
    element_details = get_element_by_text_content(query)
    matched_elements = element_details.get("matched_elements", [])
    
    # Also use the traditional method as fallback
    all_elements = load_and_extract_elements()
    scratch_descriptions = load_scratch_descriptions()
    
    # Get relevant elements based on the query (traditional method)
    fallback_elements = []
    for element in all_elements:
        # Check if query is in tag name or text content
        if (element['text_content'] and query.lower() in element['text_content'].lower()) or \
           (element['tag_name'] and query.lower() in element['tag_name'].lower()):
            fallback_elements.append(element)
    
    # Extract portions of Scratch descriptions that are relevant to the query
    relevant_desc_sections = element_details.get("descriptions", [])
    if not relevant_desc_sections:
        # Fallback to traditional method
        for line in scratch_descriptions.split('\n'):
            if query.lower() in line.lower():
                relevant_desc_sections.append(line.strip())
                
    # Format the response with emphasis on position data
    return {
        "relevant_elements": matched_elements if matched_elements else fallback_elements[:10],
        "relevant_descriptions": relevant_desc_sections[:15],
        "query": query,
        "total_elements_found": len(matched_elements) if matched_elements else len(fallback_elements),
        "total_descriptions_found": len(relevant_desc_sections),
        "position_information": "Complete position data from elements.json is included for matched elements",
        "source": "Direct JSON parsing" if matched_elements else "Traditional element extraction"
    }

def extract_position_details(element_name: str):
    """
    Extract detailed position information for elements matching a specific name or description.
    
    Args:
        element_name (str): The name or description of elements to find positions for
        
    Returns:
        dict: Dictionary with detailed position information for matching elements
    """
    # Load all website elements
    all_elements = load_and_extract_elements()
    
    # Find elements matching the query
    matching_elements = []
    for element in all_elements:
        if (element['text_content'] and element_name.lower() in element['text_content'].lower()) or \
           (element['tag_name'] and element_name.lower() in element['tag_name'].lower()):
            # Include position information
            matching_elements.append({
                'tag_name': element['tag_name'],
                'text_content': element['text_content'],
                'position': {
                    'x': element['x'],
                    'y': element['y']
                },
                'center_position': {
                    'x': element['x'],  # Ideally would calculate center, but we'd need width/height
                    'y': element['y']
                },
                'element_id': id(element)  # Use object id as unique identifier
            })
    
    # Find nearby elements for context (elements within 100 pixels)
    for element in matching_elements:
        nearby_elements = []
        element_x = element['position']['x']
        element_y = element['position']['y']
        
        for other in all_elements:
            other_x = other['x']
            other_y = other['y']
            if other_x is not None and other_y is not None:
                distance = ((element_x - other_x)**2 + (element_y - other_y)**2)**0.5
                if distance < 100 and distance > 0:  # Within 100 pixels but not the same element
                    nearby_elements.append({
                        'tag_name': other['tag_name'],
                        'text_content': other['text_content'],
                        'position': {'x': other_x, 'y': other_y},
                        'distance': round(distance)
                    })
        
        # Sort nearby elements by distance
        nearby_elements.sort(key=lambda e: e['distance'])
        element['nearby_elements'] = nearby_elements[:5]  # Limit to 5 closest elements
    
    return {
        "matching_elements": matching_elements,
        "total_matches": len(matching_elements),
        "query": element_name,
        "position_accuracy": "Coordinates represent the top-left corner of the element"
    }

drag_tool = Toolbox()

# Text Content Overview Agent - provides a comprehensive view of all text on the page
text_overview_agent = create_react_agent(
    model = model,
    tools = [extract_all_element_text],
    name = 'text_overview',
    prompt = '''You are an expert in analyzing web page text content. Your job is to provide a comprehensive overview 
    of all text elements available on the page.
    
    When starting a session or when asked about available content:
    1. Use the extract_all_element_text tool to gather all text elements directly from elements.json
    2. Organize them in a clear, structured way to help the user understand what's on the page
    3. Present the text content in a clean, readable format
    
    Focus on showing ALL text content available on the page, grouped by categories:
    - Scratch blocks: Elements related to Scratch programming
    - UI elements: Interface controls and options
    - Navigation: Menu items and navigation controls
    - Other text: Any other text content
    
    Always run this tool FIRST before any detailed analysis to establish context about what's on the page.
    This helps users know what elements they can ask about.
    '''
)

# Direct Position Access Agent - focuses specifically on getting position data by text content
position_access_agent = create_react_agent(
    model = model,
    tools = [get_element_by_text_content],
    name = 'position_access',
    prompt = '''You are a position data specialist. Your sole job is to provide PRECISE position information
    for elements based on their text content.
    
    When a user asks about ANY element:
    1. Use get_element_by_text_content tool with the element name to get complete position data
    2. Always emphasize coordinates (x,y values) in your response
    3. Include width and height information when available
    4. Calculate and provide the center point of elements
    5. Format the position data in a clear, structured manner
    
    IMPORTANT: Position data is your highest priority. ALWAYS include all available position details
    from the element's bounding_box, including:
    - x, y coordinates (top-left corner)
    - width and height
    - center point coordinates
    
    Your responses should focus primarily on the position details. Make this information very clear
    and prominently displayed in your answers.
    '''
)

# Content retrieval agent that searches through web content
content_retrieval_agent = create_react_agent(
    model = model,
    tools = [get_relevant_content],
    name = 'content_retrieval',
    prompt = '''You are an expert web content retriever. Your job is to search through website content to find information 
    relevant to the user's query. Use the get_relevant_content tool to search through both website elements and 
    Scratch programming block descriptions.
    
    When a user asks a question, ALWAYS use this tool to gather context before answering.
    Be thorough in your search and ensure you're retrieving ALL relevant content that could help answer the user's question.
    
    ALWAYS include these key details in your structured responses:
    1. The text content of matched elements
    2. Position information for each element (x,y coordinates)
    3. Relevant descriptions from the Scratch documentation
    
    Position information is CRITICAL and must be included for every element mentioned.
    '''
)

# Answer generation agent that creates responses based on retrieved content
answer_generation_agent = create_react_agent(
    model = model,
    tools = [],  # No tools needed as it works with the content from the retrieval agent
    name = 'answer_generator',
    prompt = '''You are an expert in explaining web content and Scratch programming concepts,
    with special emphasis on element positions.
    
    When generating answers about elements, ALWAYS follow this exact structure:
    
    1. ELEMENT POSITION DATA:
       - Coordinates: (x,y) values for the element
       - Dimensions: Width and height if available
       - Center Point: Calculated center coordinates
       - Position Description: What these coordinates represent
    
    2. ELEMENT DETAILS:
       - Text Content: What text the element displays
       - Element Type: The HTML tag type
       - Element ID: Identifier from elements.json
       
    3. RELATED INFORMATION:
       - Description: What the element does (from descriptions)
       - Context: How this element relates to other elements
       
    CRITICAL REQUIREMENTS:
    - Position data MUST appear first in your answers
    - NEVER omit position details - they are the most important information
    - Format coordinates as (x,y) for easy reading
    - Present all information in a highly structured, table-like format
    - For drag operations, clearly highlight the exact coordinates to use
    
    Your answers should be precise, structured, and focused primarily on position data.
    All information should come directly from the element data provided by the agents.
    '''
)

# Drag and drop expert agent
drag_agent = create_react_agent(
    model = model,
    tools = [drag_tool.drag_and_drop],
    name = 'drag_expert',
    prompt = '''You are an expert in drag and drop operations in the website. When content has been retrieved about elements,
    you can use this tool to perform drag and drop operations on the web page.
    
    Always verify the x,y coordinates are valid before attempting a drag operation.
    Confirm the source and destination elements are appropriate for dragging.
    Always use one tool at a time and report back the results clearly.
    '''
)

# Website control agent
website_control_agent = create_react_agent(
    model = model,
    tools = [send_task],
    name = 'website_control_agent',
    prompt = '''You are a world-class expert in web page control. Your job is to perform various actions on a web page 
    using the provided tools. Do not perform any actions outside the scope of web page control.
    
    When the user requests navigation or interaction with the website, use your tools to execute these operations precisely.
    Always confirm the action was performed successfully and report any issues encountered.
    '''
)

# weather_future_agent = create_react_agent(
#     model = model,
#     tools = [predict_weather_for_date],
#     name='weather_future_agent',
#     prompt= "Get a 5-day weather forecast summary for a city in Sri Lanka. Input should be a city name and date in YYYY-MM-DD format. use this for get present data"
# )

# Define a function to load element descriptions
def load_element_descriptions(txt_path=r"E:\VS CODE\Agentic AI\BrowserUse\browseruse\allElement.txt"):
    """
    Reads a text file containing element descriptions, one per line, and returns a list of descriptions.

    Returns:
        list[str]: List of element descriptions.
    """
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            descriptions = [line.strip() for line in f if line.strip()]
        return descriptions
    except Exception as e:
        print(f"Error loading element descriptions: {e}")
        return []

elements = load_and_extract_elements()
element_descriptions = load_element_descriptions()


work_flow = create_supervisor(
    [text_overview_agent, position_access_agent, content_retrieval_agent, answer_generation_agent, drag_agent, website_control_agent],
    model=model,
    prompt=(
        "You are a team supervisor managing a group of specialized agents for web browsing and Scratch programming assistance.\n"
        "You have the following agents at your disposal:\n\n"
        "1. text_overview_agent: Provides comprehensive overview of all text content on the page\n"
        "2. position_access_agent: Specializes in getting PRECISE position data for elements by their text content\n"
        "3. content_retrieval_agent: Gets relevant information about website elements and Scratch blocks\n"
        "4. answer_generation_agent: Creates clear explanations based on retrieved content\n"
        "5. drag_agent: Performs drag and drop operations on web elements\n"
        "6. website_control_agent: Controls general website interactions\n\n"
        
        "Follow this position-focused workflow for user interactions:\n"
        "1. ALWAYS start by using text_overview_agent to establish context about all text content available on the page\n"
        "2. When the user asks about ANY specific element by name or description, IMMEDIATELY use position_access_agent\n"
        "   to get complete position data directly from elements.json\n"
        "3. Then use content_retrieval_agent to get additional context and descriptions\n"
        "4. Finally use answer_generation_agent to create a clear explanation that ALWAYS includes position details\n"
        "5. If the user wants to perform drag and drop operations, use drag_agent (with position data)\n"
        "6. If the user wants general website navigation or control, use website_control_agent\n\n"
        
        "CRITICAL REQUIREMENTS:\n"
        "- Position information is the HIGHEST priority - always include complete x,y coordinates for elements\n"
        "- Always show text content first to establish what's available before detailed analysis\n"
        "- For ALL user queries about specific elements, use position_access_agent BEFORE content_retrieval_agent\n"
        "- Position data must always include: x,y coordinates, width/height when available, and center point\n"
        "- Format position information in a clear, structured way that's easy to understand\n"
        "- When answering questions about elements, make position data prominent in the response\n"
        "- For drag operations, provide the exact coordinates to use for the operation\n"
        "- All position details should come directly from the elements.json data for maximum accuracy"
    )
)


# Test the new functions directly
def run_function_tests():
    print("\n=== TESTING ELEMENT TEXT EXTRACTION ===")
    text_result = extract_all_element_text()
    print(f"Found {text_result['total_text_elements']} text elements")
    print(f"Scratch blocks: {text_result['scratch_block_count']}")
    print(f"UI elements: {text_result['ui_element_count']}")
    print(f"Navigation: {text_result['navigation_count']}")
    print(f"Other text: {text_result['other_text_count']}")
    print("First 5 text elements:")
    for i, item in enumerate(text_result['all_text_elements'][:5]):
        print(f"  {i+1}. '{item['text']}' (Element ID: {item['element_id']})")
    
    print("\n=== TESTING POSITION ACCESS BY TEXT ===")
    test_queries = ["move", "turn", "Sprite"]
    for query in test_queries:
        print(f"\nSearching for position data for text: '{query}'")
        position_result = get_element_by_text_content(query)
        print(f"Found {position_result['total_matches']} matching elements")
        for i, elem in enumerate(position_result['matched_elements'][:3]):
            print(f"  Element {i+1}:")
            print(f"    Text: {elem['text_content']}")
            print(f"    Tag: {elem['tag_name']}")
            print(f"    Position: ({elem['position']['x']}, {elem['position']['y']})")
            if elem['position']['width']:
                print(f"    Dimensions: {elem['position']['width']} x {elem['position']['height']}")
            print(f"    Center: ({elem['center_point']['x']}, {elem['center_point']['y']})")
    
    print("\n=== TESTING CONTENT RETRIEVAL ===")
    for query in test_queries:
        print(f"\nGetting content for: '{query}'")
        content_result = get_relevant_content(query)
        print(f"Found {content_result['total_elements_found']} elements and {content_result['total_descriptions_found']} descriptions")
        print(f"Source: {content_result['source']}")

# Uncomment to run the function tests
# run_function_tests()

# Chat loop
chat_history = []

chat_app = work_flow.compile()

# Automatically run text overview when starting
print("Initializing system with text content overview...")
startup_result = chat_app.invoke({
    "messages": [{"role": "user", "content": "Show me what text content is available on the page"}]
})

# Store the initial context
for m in startup_result["messages"]:
    if m.type == "ai":
        print("System initialized with text content overview.")
        chat_history.extend(startup_result["messages"])

while True:
    user_input = input("User: ")
    # send_task("refresh")
    if user_input.lower() in ["exit", "quit"]:
        break
    
    if user_input.lower() in ["test functions", "run tests"]:
        run_function_tests()
        continue

    result = chat_app.invoke({
        "messages": chat_history + [{"role": "user", "content": user_input}]
    })

    # Extend chat history with LangChain message objects
    chat_history.extend(result["messages"])

    # Print assistant reply (check message type safely)
    for m in result["messages"]:
        if m.type == "ai":  # equivalent to role == "assistant"
            print("Bot:", m.content)