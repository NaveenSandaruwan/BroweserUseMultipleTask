import os
import asyncio
from dotenv import load_dotenv
from browser_use import Agent, ChatGoogle, BrowserProfile
from browser_use.agent.service import execute_task, create_persistent_agent

# Load environment variables
load_dotenv()

# Get configuration from environment variables
USER_DATA_DIR = os.getenv("USER_DATA_DIR")
CHROME_EXECUTABLE_PATH = os.getenv("CHROME_EXECUTABLE_PATH")

# Initialize the model
llm = ChatGoogle(model='gemini-2.0-flash')

async def main():
    try:
        print("🚀 Starting persistent browser session...")
        
        # Create browser profile with keep_alive=True to maintain the session
        profile = BrowserProfile(
            user_data_dir=USER_DATA_DIR,  # your new clean profile folder
            profile="Default",
            chrome_executable_path=CHROME_EXECUTABLE_PATH,  # adjust if Chrome is elsewhere
            keep_alive=True,
            enable_default_extensions=True
        )

        # Create persistent agent with initial task
        agent = await create_persistent_agent(
            initial_task="Go to Scratch Education and create",
            llm=llm,
            browser_profile=profile
        )
        
        print("✅ Agent initialized with browser session")
        print("📝 You can now enter tasks to execute sequentially")
        print("   The browser state will persist between tasks")
        
        # Process tasks in a loop
        while True:
            task = input("\n🔷 Enter your task (or 'exit' to quit): ")
            
            if task.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Exiting and closing browser...")
                break
            
            print(f"\n🔄 Executing task: {task}")
            try:
                # Execute the task while maintaining browser state
                result = await execute_task(agent, task, max_steps=15)
                
                # Report success/failure
                if result.is_successful():
                    print(f"✅ Task completed successfully in {result.total_duration_seconds():.1f} seconds")
                else:
                    print(f"❌ Task completed without success in {result.total_duration_seconds():.1f} seconds")
                
                # Optional: Display any structured output
                if result.structured_output:
                    print("\n📊 Task output:")
                    print(result.structured_output.model_dump_json(indent=2))
                    
            except Exception as e:
                print(f"❌ Error executing task: {type(e).__name__}: {e}")
                print("The browser session is still maintained")
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error in main loop: {type(e).__name__}: {e}")
    finally:
        # Clean shutdown
        if 'agent' in locals():
            print("\n🧹 Cleaning up resources...")
            try:
                await agent.close()
                print("✅ Browser session closed successfully")
            except Exception as e:
                print(f"⚠️ Error during cleanup: {e}")
                # Force close browser if needed
                try:
                    if hasattr(agent, 'browser_session') and agent.browser_session:
                        await agent.browser_session.kill()
                        print("✅ Browser forcefully closed")
                except:
                    print("⚠️ Could not force close browser")

if __name__ == "__main__":
    asyncio.run(main())