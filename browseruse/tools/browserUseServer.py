# agent_server.py
import json
import os
import asyncio
import sys
import socket
import threading
import traceback
from dotenv import load_dotenv
from pathlib import Path

# def get_base_path():
#     """Return folder where exe/script is located (for reading/writing files)."""
#     if getattr(sys, "frozen", False):
#         # Running as PyInstaller exe
#         return Path(sys.executable).parent
#     else:
#         # Running as Python script
#         return Path(__file__).parent.parent.parent
    
# BASE_DIR = get_base_path()
# USER_DATA_DIR = BASE_DIR / "userdata" / "user_data.json"

# # Load user data from JSON file
# with open(USER_DATA_DIR, "r", encoding="utf-8") as f:
#     user_data = json.load(f)

# USER_DATA_DIR = user_data["profile_dir"]
# CHROME_EXECUTABLE_PATH = user_data["chrome_path"]

# load_dotenv()
# USER_DATA_DIR="E:\\VS CODE\\Agentic AI\\profile"
# CHROME_EXECUTABLE_PATH="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
# # BROWSER_USE_PATH = "E:\\VS CODE\\Agentic AI\\BrowserUse\\browseruse"

# # print("BROWSER_USE_PATH:", BROWSER_USE_PATH)
# sys.path.append(BROWSER_USE_PATH)
from browseruse.browser_use import ChatGoogle
from browseruse.browser_use.agent.service import execute_task, create_persistent_agent
from browseruse.browser_use.browser.permissions_manager import BrowserPermissionsManager



llm = ChatGoogle(model="gemini-2.0-flash")

task_queue = asyncio.Queue()


async def agent_worker(agent):
    """Process tasks from the queue."""
    print("📝 Agent worker started. Waiting for tasks...")
    while True:
        task = await task_queue.get()
        if task == "exit":
            print("👋 Exiting worker loop")
            task_queue.task_done()
            break

        print(f"\n🔄 Executing task: {task}")
        try:
            # Special task handling
            if task == "refresh" or task == "screenshot":
                try:
                    print("\n📸 Taking screenshot and updating DOM...")
                    
                    # Use the function to capture browser state and elements
                    from browseruse.browser_use.agent.service import capture_element_positions
                    browser_state, elements_file = await capture_element_positions(agent)
                    
                    print(f"✅ Screenshot captured with {len(browser_state.dom_state.selector_map)} elements")
                    print(f"✅ Element data stored at: {elements_file}")
                    
                except Exception as e:
                    print(f"❌ Error during refresh: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                # ADDED: Execute regular tasks through the agent
                print(f"🤖 Agent executing: {task}")
                result = await execute_task(agent, task)
                print(f"✅ Task completed: {task}")
                # Optionally print result summary
                if hasattr(result, 'output'):
                    print(f"📝 Result: {result.output[:100]}..." if len(result.output) > 100 else f"📝 Result: {result.output}")
                
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            task_queue.task_done()

def socket_listener(loop):
    """Run a socket server in a thread that pushes tasks into asyncio queue."""
    host = "127.0.0.1"
    port = 65432
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"📡 Socket server listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        with conn:
            data = conn.recv(1024).decode("utf-8").strip()
            if not data:
                continue
            print(f"📥 Received: {data}")
            asyncio.run_coroutine_threadsafe(task_queue.put(data), loop)
            conn.sendall(b"Task received\n")
            if data == "exit":
                break


async def main(CHROME_EXECUTABLE_PATH,USER_DATA_DIR):
    print("🚀 Starting agent...")
    profile = BrowserPermissionsManager.create_voice_enabled_profile(
        user_data_dir=USER_DATA_DIR,
        chrome_executable_path=CHROME_EXECUTABLE_PATH,
        keep_alive=True,
        enable_default_extensions=True,
    )
    agent = await create_persistent_agent(
        initial_task="Go to Scratch Education and create",
        llm=llm,
        browser_profile=profile,
    )
    print("✅ Agent ready")

    # Start worker
    worker = asyncio.create_task(agent_worker(agent))

    # Start socket listener in separate thread
    loop = asyncio.get_running_loop()
    threading.Thread(target=socket_listener, args=(loop,), daemon=True).start()

    # Wait for worker to finish
    await worker

    print("\n🧹 Cleaning up...")
    await agent.close()
    if hasattr(agent, "browser_session") and agent.browser_session:
        await agent.browser_session.kill()

def start_server(CHROME_EXECUTABLE_PATH, USER_DATA_DIR):
    try:
        asyncio.run(main(CHROME_EXECUTABLE_PATH, USER_DATA_DIR))
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {type(e).__name__}: {e}")
        traceback.print_exc()
    finally:
        print("🧹 Cleaning up server resources")
        # Any cleanup needed
