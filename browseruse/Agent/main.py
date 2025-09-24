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
from test import graph


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
    
  
    
    # Refresh browser state
    send_task("refresh")
    
    # Process the user input
    result = graph.invoke({
        "messages": chat_history + [{"role": "user", "content": req.message}]
    })
    
    # Update chat history
    chat_history.extend(result["messages"])
    
    # Extract messages from the format agent
    format_messages = [
        m for m in result["messages"]
        if m.type == "ai" and m.name == "format_agent" and m.content and m.content.strip()
    ]
    
    # Get the reply text
    if format_messages:
        last_format_message = format_messages[-1]
        reply_text = last_format_message.content
        print(f"Bot: {reply_text}")
    else:
        reply_text = "I'm sorry, I couldn't process your request."
        print("Bot: (no response from format agent)")
    
    print(f"[API] Sending reply: {reply_text}")
    return ChatResponse(reply=reply_text)

if __name__ == "__main__":
    import uvicorn
    print(f"[Server] Starting backend on port {BACKEND_PORT}...")
    uvicorn.run("main:app", host="127.0.0.1", port=BACKEND_PORT, reload=True)
