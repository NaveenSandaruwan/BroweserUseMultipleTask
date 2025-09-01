import asyncio
import sys
from browser_use import Agent, ChatGoogle, BrowserProfile, BrowserSession
from dotenv import load_dotenv

load_dotenv()

class BrowserAgentManager:
    """
    A manager class that creates a new agent for each task but reuses the browser session.
    This approach avoids issues with the event bus being shut down.
    """
    
    def __init__(self, llm=None, profile=None):
        self.llm = llm or ChatGoogle(model="gemini-2.0-flash")
        self.profile = profile or BrowserProfile(
            user_data_dir=r"E:\VS CODE\Agentic AI\profile",
            profile="Default",
            chrome_executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            keep_alive=True,
            enable_default_extensions=True
        )
        self.browser_session = None
        self.current_agent = None
        
    async def initialize(self):
        """Initialize the browser session."""
        if not self.browser_session:
            print("🌐 Initializing browser session...")
            self.browser_session = BrowserSession(browser_profile=self.profile)
        
    async def execute_task(self, task, max_steps=20):
        """Execute a single task using a new agent but the same browser session."""
        if not self.browser_session:
            await self.initialize()
            
        # Create a new agent for this task, sharing the browser session
        self.current_agent = Agent(
            task=task,
            llm=self.llm,
            browser_session=self.browser_session  # Reuse the browser session
        )
        
        print(f"🔄 Running task: {task}")
        result = await self.current_agent.run(max_steps=max_steps)
        return result
    
    async def run_continuous(self):
        """Run in continuous interactive mode."""
        await self.initialize()
        
        try:
            # Get initial task
            initial_task = input("\n✏️ Enter your initial task: ")
            if initial_task.lower() in ["exit", "quit", "q"]:
                print("Exiting without starting...")
                return
            
            # Execute initial task
            result = await self.execute_task(initial_task)
            print("\n✅ Task completed. Browser session remains active.")
            
            # Continue with more tasks
            while True:
                try:
                    follow_up = input("\n✏️ Enter follow-up task (or type 'exit' to quit): ")
                    
                    if follow_up.lower() in ["exit", "quit", "q"]:
                        print("Exiting continuous mode...")
                        break
                    
                    result = await self.execute_task(follow_up)
                    print("\n✅ Task completed. Browser session remains active.")
                    
                except KeyboardInterrupt:
                    print("\n⏸️ Paused. Press Ctrl+C again to exit or Enter to continue.")
                    try:
                        input()
                        continue
                    except KeyboardInterrupt:
                        print("\nExiting continuous mode...")
                        break
                except Exception as e:
                    print(f"\n❌ Error: {type(e).__name__}: {e}")
                    choice = input("Continue with next task? (y/n): ")
                    if choice.lower() != 'y':
                        break
        
        finally:
            await self.close()
    
    async def close(self):
        """Clean up resources."""
        if self.current_agent:
            try:
                # This will close the agent but not the browser session
                # since we're managing the browser session ourselves
                await self.current_agent.close()
            except Exception as e:
                print(f"Warning: Error closing agent: {e}")
            
        if self.browser_session:
            try:
                print("Closing browser session...")
                await self.browser_session.kill()
                print("Browser session closed.")
            except Exception as e:
                print(f"Warning: Error closing browser session: {e}")

async def main():
    manager = BrowserAgentManager()
    await manager.run_continuous()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
    except Exception as e:
        print(f"Fatal error: {type(e).__name__}: {e}")
        sys.exit(1)
