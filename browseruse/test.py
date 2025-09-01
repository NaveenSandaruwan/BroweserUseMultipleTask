import sys
import asyncio
from browser_use import Agent, ChatGoogle, BrowserProfile
from dotenv import load_dotenv



load_dotenv()

llm = ChatGoogle(model="gemini-2.0-flash")

async def main():
    profile = BrowserProfile(
        user_data_dir=r"C:\Users\MSI20\AppData\Local\Google\Chrome\User Data",
        profile="Default",   
    )

    agent = Agent(
        task="Go to GeeksforGeeks data structures and algorithms",
        llm=llm,
        browser_profile=profile   
    )

    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
