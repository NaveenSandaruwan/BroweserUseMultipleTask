# agent_server.py
import os
import asyncio
import sys
import socket
import threading
from dotenv import load_dotenv

sys.path.append(r"E:\VS CODE\Agentic AI\BrowserUse\browseruse")
from browser_use import ChatGoogle
from browser_use.agent.service import execute_task, create_persistent_agent
from browser_use.browser.permissions_manager import BrowserPermissionsManager

load_dotenv()
USER_DATA_DIR = os.getenv("USER_DATA_DIR")
CHROME_EXECUTABLE_PATH = os.getenv("CHROME_EXECUTABLE_PATH")

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
            result = await execute_task(agent, task, max_steps=15)
            if result.is_successful():
                print(f"✅ Success in {result.total_duration_seconds():.1f}s")
            else:
                print(f"❌ Failed in {result.total_duration_seconds():.1f}s")

            if result.structured_output:
                print("\n📊 Output:")
                print(result.structured_output.model_dump_json(indent=2))
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
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


async def main():
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


if __name__ == "__main__":
    asyncio.run(main())
