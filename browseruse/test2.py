import asyncio
from browser_use import BrowserProfile, BrowserSession, Agent, ChatGoogle

async def main():
    profile = BrowserProfile(
        executable_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        user_data_dir=r"C:\Users\MSI20\AppData\Local\Google\Chrome\User Data",
        profile_directory='Default',
    )
    try:
        browser = BrowserSession(browser_profile=profile)
        print("BrowserSession created successfully.")
        print(f"BrowserSession info: {browser}")

        # Initialize Gemini model
        llm = ChatGoogle(model='gemini-2.0-flash')
        # Create and run agent
        agent = Agent(
            task="Go to GeeksforGeeks data structures and algorithms",
            llm=llm,
            browser=browser
        )
        await agent.run()
    except Exception as e:
        print(f"Failed to create BrowserSession or run Agent: {e}")

if __name__ == "__main__":
    asyncio.run(main())
