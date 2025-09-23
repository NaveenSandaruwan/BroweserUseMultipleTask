# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from test4 import call_LLM

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

@app.post("/speak", response_model=ChatResponse)
def speak(req: ChatRequest):
    print(f"[API] Received from extension: {req.message}")
    reply_text = call_LLM(req.message)
    print(f"[API] Sending reply: {reply_text[1]}")
    return ChatResponse(reply=reply_text[1])

if __name__ == "__main__":
    import uvicorn
    print(f"[Server] Starting backend on port {BACKEND_PORT}...")
    uvicorn.run("main:app", host="127.0.0.1", port=BACKEND_PORT, reload=True)
