from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from dotenv import load_dotenv

# load_dotenv()
from utils.file_loader import load_and_extract_elements, load_scratch_descriptions
from browseruse.tools.browserUseClient import send_task
# from tools.dragTool import Toolbox
from tools.execution import Executor
import json
from difflib import SequenceMatcher



GEMINIAPI = os.getenv("GOOGLE_API_KEY") 
# print(GEMINIAPI)
# print("GEMINI_API:", GEMINIAPI)  # Debugging line to check if the API key is loaded correctly
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINIAPI,
    temperature=0.6
)

def find_closest_block(category: str, block_query: str) -> dict:
    """
    Find the closest matching block in description.json using fuzzy matching
    """
    description_path = os.getenv("ELEMENTS_DESCRIPTION_JSON_PATH")
    try:
        with open(description_path, 'r') as f:
            descriptions = json.load(f)
        
        if category in descriptions:
            best_match = None
            highest_ratio = 0
            
            # Search through all blocks in the category
            for block in descriptions[category]["blocks"]:
                # Calculate similarity ratio
                ratio = SequenceMatcher(None, 
                                      block["name"].lower(), 
                                      block_query.lower()).ratio()
                
                # Update if this is the best match so far
                if ratio > highest_ratio and ratio > 0.6:  # 0.6 threshold for minimum match
                    highest_ratio = ratio
                    best_match = block
            
            if best_match:
                # Parse coordinates
                coords = best_match["coordinates"]
                x = float(coords.split("x: ")[1].split(",")[0])
                y = float(coords.split("y: ")[1])
                
                return {
                    "name": best_match["name"],
                    "description": best_match["description"],
                    "coordinates": {"x": x, "y": y},
                    "match_confidence": highest_ratio
                }
                
    except Exception as e:
        print(f"Error finding block: {e}")
    return None
# Define custom functions to use as tools for our agents

# drag_tool = Toolbox()
executor = Executor()

# Text Content Overview Agent - provides a comprehensive view of all text on the page


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




command_agent = create_react_agent(
    model=model,
    tools=[executor.executor_tool],
    name="CommandAgent",
    prompt='''
You are a Command Agent. 
You will receive supervisor instructions about tasks to perform in Scratch.
for example 
- "I want to move this character 10 steps, repeat that 10 times, and then go to a random position."
- "Play the 'meow' sound, wait 1 second, then move 20 steps, and do this 8 times."
- "Make the sprite say 'Hello!' for 2 seconds, then turn 15 degrees to the right."
- "When the green flag is clicked, go to x:0 y:0, say 'Ready!', then move 50 steps."
- "Move the sprite 15 steps, turn 90 degrees, and repeat that sequence 4 times."

Then you will break down the instructions into discrete steps to accomplish the task using Scratch blocks.
and for each step, you will:
1. Identify the appropriate `category` and `block` needed for that step.
2. You will define a `step` only for a block and category.


Example breakdown:
Instruction: "I want to move this character 10 steps, repeat that 10 times, and then go to a random position."
Steps:
1. Get a "repeat" block from the Control category.
2. Get a "move 10 steps" block from the Motion category.
3. Get a "go to random position" block from the Motion category.

Instruction: "Play the 'meow' sound, wait 1 second, then move 20 steps, and do this 8 times."
1.Get a "repeat" block from Control.
2.Get a "play sound meow until done" block from Sound.
3.Get a "wait 1 second" block from Control.
4.Get a "move 20 steps" block from Motion.

Instruction: "Make the sprite say 'Hello!' for 2 seconds, then turn 15 degrees to the right."
1.Get a "say Hello! for 2 seconds" block from Looks.
2.Get a "turn clockwise 15 degrees" block from Motion.

Instruction: "When the green flag is clicked, go to x:0 y:0, say 'Ready!', then move 50 steps."
1.Get a "when green flag clicked" block from Events.
2.Get a "go to x:0 y:0" block from Motion.
3.Get a "say Ready! for 2 seconds" block from Looks.
4.Get a "move 50 steps" block from Motion.

Instruction: "Move the sprite 15 steps, turn 90 degrees, and repeat that sequence 4 times."
1.Get a "repeat" block from Control.
2.Get a "move 15 steps" block from Motion.
3.Get a "turn clockwise 90 degrees" block from Motion.



For each step, generate a JSON object in the following format:

{
  "steps": [
    {
      "step": 1,
      "category": "Control",
      "block": "repeat"
    },
    {
      "step": 2,
      "category": "Motion",
      "block": "move 10 steps"
    },
    {
      "step": 3,
      "category": "Motion",
      "block": "go to random position"
    }
  ]
}

Rules:
- `category` must be one of: Motion, Looks, Sound, Events, Control, Sensing, Operators, Variables.
- `block` is the Scratch block name.

Once the JSON is generated, send it to the `executor_tool` for execution.
Once the JSON is generated, send it to the `executor_tool` for execution.
Once the JSON is generated, send it to the `executor_tool` for execution.

Output:
- Only the JSON object.
- Nothing else except calling the `executor_tool` with the JSON object.
- Nothing else except calling the `executor_tool` with the JSON object.
'''
)



work_flow = create_supervisor(
    [command_agent],
    model=model,
    prompt=(
        '''
        You are a Scratch programming expert and know everything about Scratch programming blocks, their categories, and how they should be used to create programs.
        You are a Supervisor Agent responsible for interpreting user instructions and directly forwarding them to the CommandAgent.

        Your job is to:
        1..Directly forward user instructions to the CommandAgent without any modifications.

    

        For example:
        If the user says, "I want to move this character 10 steps, repeat that 10 times, and then go to a random position," you should directly forward this instruction to the CommandAgent.
        list of example user requests:
        - "Play the 'meow' sound, wait 1 second, then move 20 steps, and do this 8 times."
        - "Make the sprite say 'Hello!' for 2 seconds, then turn 15 degrees to the right."
        - "When the green flag is clicked, go to x:0 y:0, say 'Ready!', then move 50 steps."
        - "Move the sprite 15 steps, turn 90 degrees, and repeat that sequence 4 times."

        Do not output anything else except the user's instruction to the CommandAgent.
        your job is only to forward the user's instruction to the CommandAgent.
        then the CommandAgent will handle the rest.
        '''
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

# Store the initial context

while True:
    user_input = input("User: ")
    # send_task("refresh")

    result = chat_app.invoke({
        "messages": chat_history + [{"role": "user", "content": user_input}]
    })

    # Extend chat history with LangChain message objects
    chat_history.extend(result["messages"])

    # Print assistant reply (check message type safely)
    for m in result["messages"]:
        if m.type == "ai":  # equivalent to role == "assistant"
            print("Bot:", m.content)