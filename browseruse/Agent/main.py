# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agent import chat
from emotion import EmotionIdentifier

BACKEND_PORT = 5000  # your port
chat_history = []
detector = EmotionIdentifier()

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
    Expects JSON: {"message": "..."}
    Sends JSON: {"reply": "...", "emotion": "..."}
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            user_message = data.get("message", "")

            # Update chat history
            # chat_history.append({"role": "user", "content": user_message})

            # Chat reply
            chat_result = chat.invoke({"query": user_message})
            reply_text = chat_result['result']['formatted_response']

            # Emotion detection (using last 3 messages)
            # history_to_use = chat_history[-3:] if len(chat_history) > 3 else chat_history
            # history_text = "\n".join([
            #     f"{'User' if msg.get('role') == 'user' else 'Assistant'}: {msg.get('content', '')}"
            #     for msg in history_to_use
            # ])
            emotion = detector.identify_emotion(user_message)

            # Send combined response
            await websocket.send_json({
                "reply": reply_text,
                "emotion": emotion
            })
            print(f"[WebSocket] Sent reply: {reply_text} with emotion: {emotion}")

    except WebSocketDisconnect:
        print("Client disconnected")


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Server is healthy"}


if __name__ == "__main__":
    import uvicorn

    print(f"[Server] Starting backend on ws://127.0.0.1:{BACKEND_PORT} ...")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=BACKEND_PORT,
        reload=True
    )
