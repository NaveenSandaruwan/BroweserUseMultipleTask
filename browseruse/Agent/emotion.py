import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi import FastAPI, Request
from pydantic import BaseModel

load_dotenv()

GEMINIAPI = os.getenv("GOOGLE_API_KEY")

class EmotionIdentifier:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
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
            "Respond with only one word (e.g., happy, sad, angry, surprised, fearful, disgusted, neutral).\n\n"
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
