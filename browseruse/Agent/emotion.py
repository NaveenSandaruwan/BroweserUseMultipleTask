import json
import os
import sys
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from pathlib import Path
# load_dotenv()
def get_base_path():
    """Return folder where exe/script is located (for reading/writing files)."""
    if getattr(sys, "frozen", False):
        # Running as PyInstaller exe
        return Path(sys.executable).parent
    else:
        # Running as Python script
        return Path(__file__).parent.parent.parent

BASE_DIR = get_base_path()
USER_DATA_DIR = BASE_DIR / "userdata" / "user_data.json"

# Load user data from JSON file
with open(USER_DATA_DIR, "r", encoding="utf-8") as f:
    user_data = json.load(f)



GEMINIAPI = user_data['gemini_api_key']

class EmotionIdentifier:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINIAPI,
            temperature=0.3
        )

    def identify_emotion(self, text: str, history: str = "") -> str:
        """
        Identifies the emotion expressed in the input text using Gemini.
        Optionally includes previous conversation history in the prompt.
        Returns a string representing the detected emotion.
        """
        prompt = (
            "Identify the primary emotion expressed in the following text. "
            "Imagine you are in conversation with a child. And you have to identify the emotion should react from their text.\n"
            "Respond with only one word by most suitable emotion from here happy, sad, angry, surprised, fearful, disgusted, neutral.\n\n"
            "Imagine you are a learning assistant for children. "
            "You have to identify the reaction emotion of the user from their text.\n"
        )
        if history:
            prompt += f"Conversation history:\n{history}\n"
        prompt += f'Text: "{text}"\nEmotion:'

        response = self.model.invoke(prompt)
        emotion = response.content.strip().lower()
        return emotion



# Example usage
# if __name__ == "__main__":
#     detector = EmotionIdentifier()
#     user_input = input("Enter text: ")
#     emotion = detector.identify_emotion(user_input)
#     print(f"Detected emotion: {emotion}")
