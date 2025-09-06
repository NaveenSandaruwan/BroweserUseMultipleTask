import os
import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')

app = FastAPI()

# Allow CORS for local extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    text: str

# System prompt to help Gemini understand command structure
SYSTEM_PROMPT = """You are an AI assistant that can both answer questions and control an avatar on the screen.
When users ask general questions, respond normally.
When users ask you to perform actions, respond with a JSON command structure.

Commands available:
1. Move avatar: When asked to move, respond with:
   {"type": "command", "action": "move", "x": <x_position>, "y": <y_position>}

For movement commands:
- x and y should be between 0 and 1000
- Interpret relative positions like "left", "right", "top", "bottom"
- "left" = x:100, "right" = x:900, "top" = y:100, "bottom" = y:900
- "center" = x:500, y:500

Examples:
User: "Move to the right"
Response: {"type": "command", "action": "move", "x": 900, "y": 500}

User: "What is Python?"
Response: {"type": "response", "text": "Python is a high-level programming language..."}

Always respond with valid JSON containing either a command or a response."""

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_text = req.text.strip()
    if not user_text:
        return {"type": "response", "text": "Please say something!"}
    
    try:
        # Create chat with system prompt
        chat = model.start_chat(history=[])
        
        # Send system prompt and user message
        response = chat.send_message(f"{SYSTEM_PROMPT}\n\nUser: {user_text}")
        
        try:
            # Try to parse as JSON
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError:
            # If not valid JSON, treat as regular response
            return {
                "type": "response",
                "text": response.text
            }
            
    except Exception as e:
        return {
            "type": "response",
            "text": f"Sorry, I had an error: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)