# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
  # Implement custom call_LLM logic directly here
from tools.browserUseClient import send_task
# from test4 import chat_app
from test3 import ScratchChatApp
from tools.filter import filter_json, find_used_blocks, get_list_of_used_blocks, get_category_coordinates, generate_detailed_blocks_summary

import time

from emotion import EmotionIdentifier

load_dotenv()

BACKEND_PORT = 5000  # choose your port

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

# def run_llm(user_message: str) -> str:
#     """Simple stub LLM reply"""
#     print(f"[LLM] Received: {user_message}")
#     reply = f"AI says: I heard '{user_message}'. This is my response."
#     print(f"[LLM] Reply: {reply}")
#     return reply
chat_history = []

@app.post("/speak", response_model=ChatResponse)
def speak(req: ChatRequest):
    print(f"[API] Received from extension: {req.message}")

    # Import the required class and functions

    # Initialize the chat app instance (or use a singleton/global if needed)
    scratch_chat_app = ScratchChatApp()

    # Refresh browser state
    scratch_chat_app.send_task("refresh")
    time.sleep(2)  # wait for the page to load
    # Update working space and context
    scratch_chat_app.working_space = get_list_of_used_blocks()
    scratch_chat_app.context = filter_json()
    print(scratch_chat_app.working_space)

    # Process the user input
    result = scratch_chat_app.invoke({
        "messages": scratch_chat_app.chat_history + [{"role": "user", "content": req.message}]
    })

    # Extend chat history with LangChain message objects
    scratch_chat_app.chat_history.extend(result["messages"])

    # Print only the last AI message
    responses = {
            "supervisor": None,
            "format_agent": None,
            "coordinate_expert": None,
            "debugging_expert": None,
            "coding_expert": None
        }

    for message in result["messages"]:
        # AI/Tool messages will have .name
        if hasattr(message, "name") and message.name in responses:
            responses[message.name] = message.content

    # Check if format agent has a result
    if responses["format_agent"] and len(responses["format_agent"]) > 200:
        reply_text = responses["format_agent"]
        print("Bot:", reply_text)
    else:
        # Pick the longest response among other agents
        longest_response = max(
            (resp for role, resp in responses.items() if role != "format_agent" and resp),
            key=len,
            default=None
        )
        if longest_response:
            reply_text = longest_response
            print("Bot:", reply_text)
        else:
            ai_messages = [m for m in result["messages"] if m.type == "ai"]
            if ai_messages:
                reply_text = ai_messages[-1].content
                print("Bot:", reply_text)
            else:
                print("Bot: (No response found)")

    print(f"[API] Sending reply: {reply_text}")
    return ChatResponse(reply=reply_text)

class EmotionRequest(BaseModel):
    text: str
detector = EmotionIdentifier()

@app.post("/emotion")
async def emotion_endpoint(request: EmotionRequest):
    # Format chat history if needed
    history_text = ""
    if  chat_history:
        # Use only the last 3 entries if history is longer than 3
        history_to_use = chat_history[-3:] if len(chat_history) > 3 else chat_history
        
        # Convert chat history to a readable format
        history_text = "\n".join([
            f"{'User' if getattr(msg, 'type', None) == 'human' else 'Assistant'}: {getattr(msg, 'content', '')}"
            for msg in history_to_use if hasattr(msg, 'content')
        ])
        print(f"Formatted history for emotion detection:\n{history_text}")
    # Pass the formatted history to the emotion identifier
    emotion = detector.identify_emotion(request.text, history=history_text)
    return {"emotion": emotion}


if __name__ == "__main__":
    import uvicorn

    print(f"[Server] Starting backend on port {BACKEND_PORT}...")
    uvicorn.run("main:app", host="127.0.0.1", port=BACKEND_PORT, reload=True)
