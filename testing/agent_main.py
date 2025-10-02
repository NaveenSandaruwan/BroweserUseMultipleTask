# --- START OF test_main.py ---

import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

# 1. CRITICAL FIX: Use a RAW STRING (r"...") for the Windows path.
target_dir = r"C:\Users\malit\OneDrive\Desktop\OBO\BroweserUseMultipleTask\browseruse\Agent"

# 2. Add the target directory to Python's search path
if target_dir not in sys.path:
    sys.path.insert(0, target_dir)
    print(f"Added to sys.path: {target_dir}") 

# 3. Now the imports from 'main' will work
# NOTE: This assumes 'agent.py' and 'emotion.py' are also accessible 
# from the 'Agent' directory or its siblings/parent, as 'main.py' imports them.
from main import app, ChatResponse, detector, chat_history

# ==============================================================================
# Pytest Fixtures and Mocks (as previously provided)
# ==============================================================================

@pytest.fixture(scope="module")
def client():
    # Clear the global chat history before testing starts
    chat_history.clear()
    with TestClient(app) as c:
        yield c

@pytest.fixture
def mock_agent_chat_invoke():
    """Mocks the chat.invoke method used in the /speak endpoint."""
    with patch('main.chat') as mock_chat:
        mock_chat.invoke.return_value = {
            'result': {
                'formatted_response': "AI says: This is the mock LLM response."
            }
        }
        yield mock_chat 

@pytest.fixture
def mock_emotion_detection():
    """Mocks the detector.identify_emotion method."""
    with patch('main.detector') as mock_detector:
        mock_detector.identify_emotion.return_value = "happy"
        yield mock_detector 

# ==============================================================================
# TESTS (as previously provided)
# ==============================================================================

# def test_root_status(client):
#     """Test the basic status of the app (FastAPI default)."""
#     response = client.get("/")
#     assert response.status_code == 200

def test_speak_success(client, mock_agent_chat_invoke):
    """Test /speak endpoint with a simple request and check mock usage."""
    chat_history.clear() 
    user_message = "Hello, what can you do?"
    response = client.post("/speak", json={"message": user_message})
    assert response.status_code == 200
    data = ChatResponse(**response.json())
    assert data.reply == "AI says: This is the mock LLM response."
    mock_agent_chat_invoke.invoke.assert_called_once()

def test_emotion_success_no_history(client, mock_emotion_detection):
    """Test /emotion endpoint with no prior chat history."""
    chat_history.clear() 
    user_text = "I feel amazing today!"
    response = client.post("/emotion", json={"text": user_text})
    assert response.status_code == 200
    assert response.json()["emotion"] == "happy"
    mock_emotion_detection.identify_emotion.assert_called_once_with(user_text, history="")

def test_emotion_success_with_history(client, mock_emotion_detection):
    """Test /emotion endpoint with existing chat history."""
    chat_history.clear()
    mock_history_objects = [
        MagicMock(type="human", content="I hate this project."), 
        MagicMock(type="assistant", content="What is bothering you?"), 
        MagicMock(type="human", content="It's just so frustrating."), 
        MagicMock(type="assistant", content="I understand. Let's try to fix it."), 
    ]
    chat_history[:] = mock_history_objects 
    user_text = "I am so done with this."
    expected_history_text = "\n".join([
        "Assistant: What is bothering you?",
        "User: It's just so frustrating.",
        "Assistant: I understand. Let's try to fix it."
    ])
    response = client.post("/emotion", json={"text": user_text})
    assert response.status_code == 200
    mock_emotion_detection.identify_emotion.assert_called_once_with(
        user_text, 
        history=expected_history_text
    )

def test_emotion_invalid_input(client):
    """Test /emotion endpoint with invalid input (missing 'text')."""
    response = client.post("/emotion", json={"message": "wrong key"}) 
    assert response.status_code == 422 
    data = response.json()
    assert "detail" in data 
    error_messages = [item["msg"].lower() for item in data["detail"]]
    assert "field required" in error_messages
    
