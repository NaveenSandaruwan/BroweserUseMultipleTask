# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import traceback
from typing import Dict, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from browseruse.Agent.agent import chat
from browseruse.Agent.emotion import EmotionIdentifier

BACKEND_PORT = 5000  # your port
chat_history = []
detector = EmotionIdentifier()

# Store recent emotions to avoid duplicating work
recent_emotions: Dict[str, str] = {}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for chat and emotion detection.
    Expects JSON: {"type": "chat|emotion", "message": "..."}
    Sends JSON: {"reply": "...", "emotion": "..."} or {"emotion": "..."}
    """
    await websocket.accept()
    try:
        while True:
            # Receive and parse the WebSocket message
            data = await websocket.receive_json()
            request_type = data.get("type", "chat")  # Default to chat if type not specified
            user_message = data.get("message", "")
            
            # Validate the message
            if not user_message:
                await websocket.send_json({
                    "type": "error",
                    "error": "No message provided"
                })
                continue

            print(f"[WebSocket] Received {request_type} request: '{user_message[:30]}...'")

            try:
                if request_type == "chat":
                    # Check if we have already detected the emotion for this message
                    emotion = recent_emotions.get(user_message, None)
                    
                    # If emotion was not previously detected, get it now
                    if emotion is None:
                        emotion = detector.identify_emotion(user_message)
                        print(f"[WebSocket] Chat: Detected new emotion: {emotion}")
                    else:
                        print(f"[WebSocket] Chat: Using cached emotion: {emotion}")
                        # Remove from cache after use
                        del recent_emotions[user_message]
                    
                    # Now get the chat reply using the agent (which takes longer)
                    chat_result = chat.invoke({"query": user_message})
                    reply_text = chat_result['result']['formatted_response']

                    # Send combined response with both reply and emotion
                    await websocket.send_json({
                        "type": "chat",
                        "reply": reply_text,
                        "emotion": emotion
                    })
                    print(f"[WebSocket] Chat: Sent reply with emotion: {emotion}")
                
                elif request_type == "emotion":
                    # Handle emotion-only request
                    emotion = detector.identify_emotion(user_message)
                    
                    # Cache the emotion for later use
                    recent_emotions[user_message] = emotion
                    
                    # Send emotion-only response
                    await websocket.send_json({
                        "type": "emotion",
                        "emotion": emotion
                    })
                    print(f"[WebSocket] Emotion: Detected '{emotion}' for message")
                    
                    # Clean cache after 5 minutes (not implemented for simplicity)
                    # In a production environment, you'd want to implement a timeout mechanism
                
                else:
                    # Unknown request type
                    await websocket.send_json({
                        "type": "error",
                        "error": f"Unknown request type: {request_type}"
                    })
                    print(f"[WebSocket] Error: Unknown request type: {request_type}")
            
            except Exception as e:
                # Handle errors in processing
                error_message = f"Error processing {request_type} request: {str(e)}"
                traceback_str = traceback.format_exc()
                print(f"[WebSocket] {error_message}\n{traceback_str}")
                
                await websocket.send_json({
                    "type": "error",
                    "error": error_message
                })

    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected")


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Server is healthy"}


# if __name__ == "__main__":
#     try:
#         import uvicorn
#     except ImportError:
#         print("uvicorn not found. Please install it with: pip install uvicorn")
#         print("Or: pip install -r requirements.txt")
#         import sys
#         sys.exit(1)

#     print(f"[Server] Starting backend on ws://127.0.0.1:{BACKEND_PORT} ...")
#     uvicorn.run(
#         "main:app",
#         host="127.0.0.1",
#         port=BACKEND_PORT,
#         reload=True
#     )


def start_agent_server():
    try:
        import uvicorn
    except ImportError:
        print("uvicorn not found. Please install it with: pip install uvicorn")
        print("Or: pip install -r requirements.txt")
        import sys
        sys.exit(1)

    print(f"[Server] Starting backend on ws://127.0.0.1:{BACKEND_PORT} ...")
    uvicorn.run(
        app,  # Pass the app object directly
        host="127.0.0.1",
        port=BACKEND_PORT,
        reload=False  # Disable reload for compiled executables
    )
# if __name__ == "__main__":
#     start_agent_server()