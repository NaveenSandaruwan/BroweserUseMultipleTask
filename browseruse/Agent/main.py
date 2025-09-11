from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from agent import agent  # your compiled LangGraph agent

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # adjust for production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Input model from frontend
class UserMessage(BaseModel):
    text: str


def ask(msg):
    try:
        # Initialize agent state with "question"
        initial_state = {"question": msg.text}

        # Invoke the agent
        result_state = agent.invoke(initial_state)

        # Extract answer safely
        answer = result_state.get("answer", "Sorry, something went wrong with the agent.")

        # Ensure structured JSON command format
        structured_command = {
            "action": "explain",
            "text": answer
        }

        # Optionally, include coordinates if your agent adds them
        if "x" in result_state and "y" in result_state:
            structured_command["x"] = result_state["x"]
            structured_command["y"] = result_state["y"]
        if "id" in result_state:
            structured_command["id"] = result_state["id"]

        return {"status": "ok", "command": structured_command}

    except Exception as e:
        # Return fallback structured command in case of error
        return {
            "status": "error",
            "command": {"action": "explain", "text": "Sorry, something went wrong with the agent."},
            "error": str(e)
        }
    

print(ask(UserMessage(text="What is move button?")))
