import sys
import asyncio
from browser_use import Agent, ChatGoogle, BrowserProfile
from dotenv import load_dotenv
# Import the QueueShutDown exception to handle it specifically
from bubus.service import QueueShutDown
import os

load_dotenv()

llm = ChatGoogle(model="gemini-2.0-flash")
USER_DATA_DIR = os.getenv("USER_DATA_DIR")
CHROME_EXECUTABLE_PATH = os.getenv("CHROME_EXECUTABLE_PATH")
async def main():
    try:
        profile = BrowserProfile(
            user_data_dir=USER_DATA_DIR,  # your new clean profile folder
            profile="Profile 1",
            chrome_executable_path=CHROME_EXECUTABLE_PATH, # adjust if Chrome is elsewhere
            keep_alive=True,
            enable_default_extensions=True
        )

        agent = Agent(
            task="Go to Scratch Education and create",
            llm=llm,
            browser_profile=profile
        )

        try:
            # Use the continuous_browser_control with initial task
            await agent.continuous_browser_control(
                initial_task="Go to Scratch Education and create", 
                max_steps_per_task=5
            )
        except QueueShutDown:
            print("\n⚠️ Event queue was shut down. This is a known issue with continuous operation.")
            print("If you want to continue, please restart the script.")
        except Exception as e:
            print(f"\n❌ Error during continuous control: {type(e).__name__}: {e}")
        finally:
            # Always try to clean up properly
            try:
                await agent.close()
                print("Agent resources cleaned up.")
            except Exception as cleanup_error:
                print(f"Warning: Could not clean up agent resources: {cleanup_error}")
    
    except Exception as e:
        print(f"Fatal error: {type(e).__name__}: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
