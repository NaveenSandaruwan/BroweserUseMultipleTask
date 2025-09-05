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
        print("🚀 Starting persistent browser session with permissions management...")
        
        # Create browser profile using the permissions manager with microphone enabled by default
        # This will use the correct CDP permission name 'audioCapture' for microphone access
        profile = BrowserPermissionsManager.create_voice_enabled_profile(
            user_data_dir=USER_DATA_DIR,  # your profile folder
            chrome_executable_path=CHROME_EXECUTABLE_PATH,  # adjust if Chrome is elsewhere
            keep_alive=True,
            enable_default_extensions=True
        )

        print(f"🔓 Starting with permissions: {profile.permissions}")
        
        # Create persistent agent with initial task
        agent = await create_persistent_agent(
            initial_task="Get familiar with this page",
            llm=llm,
            browser_profile=profile
        )
        
        print("✅ Agent initialized with browser session")
        print("📝 You can now enter tasks to execute sequentially")
        print("🔐 You can also manage permissions with special commands")
        
        # Show available commands
        print("\n📋 Special Commands:")
        print("  - 'exit': Quit the program")
        print("  - 'refresh': Update browser state after manual navigation")
        print("  - 'perms show': Show current permissions")
        print("  - 'perms add <permission>': Add a specific permission")
        print("  - 'perms preset <preset>': Use a permission preset (default, media, location, full)")
        print("  - 'perms reset': Reset all permissions")
        print("\n🔑 Available permissions: microphone (audioCapture), camera (videoCapture), geolocation, notifications, clipboardReadWrite")
        
        # Process tasks in a loop
        while True:
            task = input("\n🔷 Enter your task or command: ")
            
            if task.lower() == 'exit':
                print("\n👋 Exiting and closing browser...")
                break
            
            elif task.lower() == 'refresh':
                print("\n🔄 Refreshing browser state after manual navigation...")
                result = await execute_task(agent, "This page changed, get familiar with it", max_steps=15)
                print("✅ Browser state refreshed - the agent now knows the current page state")
                continue
            
            elif task.lower() == 'perms show':
                try:
                    current_permissions = BrowserPermissionsManager.get_current_permissions(agent.browser_session)
                    
                    # Create a more user-friendly display with common names
                    user_friendly = []
                    reverse_map = {v: k for k, v in BrowserPermissionsManager.PERMISSION_MAP.items()}
                    
                    for perm in current_permissions:
                        if perm in reverse_map:
                            user_friendly.append(f"{reverse_map[perm]} ({perm})")
                        else:
                            user_friendly.append(perm)
                    
                    print(f"\n🔐 Current permissions: {', '.join(user_friendly) if user_friendly else 'None'}")
                except Exception as e:
                    print(f"❌ Error fetching permissions: {e}")
                continue
            
            elif task.lower().startswith('perms add '):
                # Extract permission name
                permission = task.lower().replace('perms add ', '').strip()
                
                # Check if it's a legacy name that needs to be mapped
                if permission in BrowserPermissionsManager.PERMISSION_MAP:
                    cdp_permission = BrowserPermissionsManager.PERMISSION_MAP[permission]
                    print(f"ℹ️ Using CDP permission name: '{cdp_permission}' for '{permission}'")
                elif permission in BrowserPermissionsManager.AVAILABLE_PERMISSIONS:
                    cdp_permission = permission
                else:
                    cdp_permission = None
                
                if cdp_permission:
                    try:
                        current_permissions = BrowserPermissionsManager.get_current_permissions(agent.browser_session)
                        if cdp_permission not in current_permissions:
                            # Add the new permission
                            new_permissions = current_permissions + [cdp_permission]
                            
                            # Grant the new permission
                            await BrowserPermissionsManager.grant_permissions(
                                agent.browser_session,
                                permissions=[permission]  # The grant_permissions method will handle conversion
                            )
                            
                            # Update the profile's permission list
                            agent.browser_session.browser_profile.permissions = new_permissions
                            
                            print(f"✅ Added permission: {permission} (CDP: {cdp_permission})")
                            print(f"🔐 Current permissions: {new_permissions}")
                        else:
                            print(f"ℹ️ Permission '{permission}' is already granted")
                    except Exception as e:
                        print(f"❌ Error adding permission: {e}")
                else:
                    print(f"❌ Unknown permission: '{permission}'")
                    print(f"🔑 Available permissions: microphone (audioCapture), camera (videoCapture), geolocation, notifications, clipboardReadWrite")
                    print(f"🔍 For a complete list, see the BrowserPermissionsManager.AVAILABLE_PERMISSIONS")
                continue
            
            elif task.lower().startswith('perms preset '):
                # Extract preset name
                preset = task.lower().replace('perms preset ', '').strip()
                if preset in BrowserPermissionsManager.PRESETS:
                    try:
                        # Get the preset permissions
                        preset_permissions = BrowserPermissionsManager.PRESETS[preset]
                        
                        # Grant all permissions in the preset
                        await BrowserPermissionsManager.grant_permissions(
                            agent.browser_session,
                            permissions=preset_permissions
                        )
                        
                        # Update the profile's permission list
                        agent.browser_session.browser_profile.permissions = preset_permissions
                        
                        print(f"✅ Applied preset '{preset}'")
                        print(f"🔐 Current permissions: {preset_permissions}")
                    except Exception as e:
                        print(f"❌ Error applying preset: {e}")
                else:
                    print(f"❌ Unknown preset: '{preset}'")
                    print(f"🔑 Available presets: {', '.join(BrowserPermissionsManager.PRESETS.keys())}")
                continue
            
            elif task.lower() == 'perms reset':
                try:
                    # Reset all permissions
                    await BrowserPermissionsManager.reset_permissions(agent.browser_session)
                    
                    # Update the profile's permission list to defaults
                    default_permissions = ['clipboardReadWrite', 'notifications']
                    agent.browser_session.browser_profile.permissions = default_permissions
                    
                    print("✅ Reset all permissions to defaults")
                    print(f"🔐 Current permissions: {default_permissions}")
                except Exception as e:
                    print(f"❌ Error resetting permissions: {e}")
                continue
                
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
