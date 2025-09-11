import os
import asyncio
from dotenv import load_dotenv
from browser_use import Agent, ChatGoogle, BrowserProfile
from browser_use.agent.service import execute_task, create_persistent_agent
from browser_use.browser.permissions_manager import BrowserPermissionsManager

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
        
        # Create browser profile with permissions manager
        # Use the convenience method for voice-enabled applications
        profile = BrowserPermissionsManager.create_voice_enabled_profile(
            user_data_dir=USER_DATA_DIR,  # your new clean profile folder
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
        print("🔐 You can also manage permissions with commands like 'perms mic'")
        
        # Process tasks in a loop
        # Example usage in your script
        while True:
            task = input("\n🔷 Enter your task (or 'refresh' to update browser state, 'perms help' for permissions, 'exit' to quit): ")
            
            if task.lower() == 'exit':
                print("\n👋 Exiting and closing browser...")
                break
            elif task.lower() == 'refresh':
                print("\n🔄 Refreshing browser state after manual navigation...")
                result = await execute_task(agent, "This page changed, get familiar with it", max_steps=5)
                print("✅ Browser state refreshed - the agent now knows the current page state")
                continue
            elif task.lower() == 'perms help':
                print("\n🔐 Permission Commands:")
                print("  - 'perms show': Show current permissions")
                print("  - 'perms mic': Enable microphone")
                print("  - 'perms camera': Enable camera")
                print("  - 'perms geo': Enable geolocation")
                print("  - 'perms media': Enable all media permissions (mic+camera)")
                print("  - 'perms reset': Reset to default permissions")
                continue
            elif task.lower() == 'perms show':
                print(f"\n🔐 Current permissions: {agent.browser_session.browser_profile.permissions}")
                continue
            elif task.lower() in ['perms mic', 'perms microphone']:
                try:
                    await BrowserPermissionsManager.grant_permissions(
                        agent.browser_session, ['microphone']
                    )
                    print("✅ Microphone permission granted")
                except Exception as e:
                    print(f"❌ Error granting permission: {e}")
                continue
            elif task.lower() in ['perms camera', 'perms cam']:
                try:
                    await BrowserPermissionsManager.grant_permissions(
                        agent.browser_session, ['camera']
                    )
                    print("✅ Camera permission granted")
                except Exception as e:
                    print(f"❌ Error granting permission: {e}")
                continue
            elif task.lower() in ['perms geo', 'perms geolocation']:
                try:
                    await BrowserPermissionsManager.grant_permissions(
                        agent.browser_session, ['geolocation']
                    )
                    print("✅ Geolocation permission granted")
                except Exception as e:
                    print(f"❌ Error granting permission: {e}")
                continue
            elif task.lower() in ['perms media']:
                try:
                    await BrowserPermissionsManager.grant_permissions(
                        agent.browser_session, ['microphone', 'camera']
                    )
                    print("✅ All media permissions granted (microphone, camera)")
                except Exception as e:
                    print(f"❌ Error granting permissions: {e}")
                continue
            elif task.lower() == 'perms reset':
                try:
                    await BrowserPermissionsManager.reset_permissions(agent.browser_session)
                    # Re-grant default permissions
                    await BrowserPermissionsManager.grant_permissions(
                        agent.browser_session, ['clipboardReadWrite', 'notifications']
                    )
                    print("✅ Permissions reset to defaults")
                except Exception as e:
                    print(f"❌ Error resetting permissions: {e}")
                continue
            
            print(f"\n🔄 Executing task: {task}")
            # Execute task as before...
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
                if hasattr(agent, 'browser_session') and agent.browser_session:
                    await agent.browser_session.kill()
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