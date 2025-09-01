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
        user_data_dir=r"E:\VS CODE\Agentic AI\profile",  
        profile="Default",
        chrome_executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        keep_alive=True,
        enable_default_extensions=True
    )
    browser = BrowserSession(
        browser_profile=profile
    )
    agent = Agent(
        task="Go to geeks for geeks data structures and algorithms",
        llm=llm,
        browser=browser
    )
    
    try:
        while True:
            task = input("Enter a task (or 'exit' to quit): ")
            if task.lower() == "exit":
                print("Exiting program...")
                try:
                    await agent.shutdown()
                except Exception as e:
                    print(f"Error during shutdown: {e}")
                    print("Forcing browser closure...")
                    # Last resort attempt to close browser
                    if hasattr(agent, 'browser_session') and agent.browser_session:
                        if hasattr(agent.browser_session, 'browser') and agent.browser_session.browser:
                            try:
                                await agent.browser_session.browser.close()
                                print("Browser closed forcefully.")
                            except:
                                print("Could not close browser.")
                break
            else:
                await agent.process_one_task(task)
    except KeyboardInterrupt:
        print("\nProgram interrupted. Shutting down...")
        try:
            await agent.shutdown()
        except Exception as e:
            print(f"Error during shutdown after interrupt: {e}")
    except Exception as e:
        print(f"Error in main loop: {e}")
        print("Attempting clean shutdown...")
        try:
            await agent.shutdown()
        except Exception as shutdown_e:
            print(f"Error during emergency shutdown: {shutdown_e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())





