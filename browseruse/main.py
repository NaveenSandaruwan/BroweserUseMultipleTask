from browser_use import Agent, ChatGoogle, BrowserProfile, BrowserSession ,browser
from dotenv import load_dotenv

# Read GOOGLE_API_KEY into env
load_dotenv()

# Create a browser profile


# Start a browser session using the browser_profile argument


# Initialize the model
llm = ChatGoogle(model='gemini-2.0-flash')

# Create agent with the model


import asyncio

load_dotenv()


async def main():
    profile = BrowserProfile(
    
    user_data_dir='C:\\Users\\MSI20\\AppData\\Local\\Google\\Chrome\\User Data',
    profile_directory='Default',
        )
    browser = BrowserSession(
    browser_profile=profile
     )
    agent = Agent(
    task="Go to geeks for geeks data structures and algorithms",
    llm=llm,
    browser=browser
            )
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())





