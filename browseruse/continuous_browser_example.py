import asyncio
from browser_use import Agent, ChatGoogle, BrowserProfile
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM
llm = ChatGoogle(model="gemini-2.0-flash")

# Browser profile setup
profile = BrowserProfile(
    user_data_dir=r"E:\VS CODE\Agentic AI\profile",  
    profile="Default",
    chrome_executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    keep_alive=True,
    enable_default_extensions=True
)

async def main():
    print("🌐 Starting continuous browser interaction example")
    
    # Create the agent with your initial task
    agent = Agent(
        task="",  # Will be set by continuous_browser_control
        llm=llm,
        browser_profile=profile
    )
    
    # Start continuous browser control with an initial task
    await agent.continuous_browser_control(
        initial_task="Go to GeeksforGeeks and find an article about data structures",
        max_steps_per_task=15
    )
    
    # When continuous_browser_control exits, clean up
    await agent.close()
    print("✅ Example complete")

if __name__ == "__main__":
    asyncio.run(main())
