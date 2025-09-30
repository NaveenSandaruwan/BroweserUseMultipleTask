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

# drag_tool = Toolbox()
executor = Executor()




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


# Chat loop
chat_history = []

chat_app = work_flow.compile()



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