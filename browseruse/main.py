import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from browseruse.tools.browserUseClient import send_task
from browseruse.tools.browserUseServer import start_server
import threading
import multiprocessing


import asyncio
import multiprocessing
import socket
import sys
import time



# ----------------------------
# Helper: wait for server ready
# ----------------------------
def wait_for_server(host="127.0.0.1", port=65432, timeout=30):
    """Wait until the server socket is open, or timeout."""
    for i in range(timeout):
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f"✅ Server is ready after {i+1}s")
                return True
        except (OSError, ConnectionRefusedError):
            print("⏳ Waiting for server...")
            time.sleep(1)
    return False


# ----------------------------
# Main entrypoint
# ----------------------------
if __name__ == "__main__":
    # Required for PyInstaller + multiprocessing on Windows
    multiprocessing.freeze_support()

    # 1. Start server process
    browseruse_server_process = multiprocessing.Process(target=start_server)
    browseruse_server_process.start()

    # 2. Wait until server is listening
    if not wait_for_server():
        print("❌ Server did not start in time")
        browseruse_server_process.terminate()
        sys.exit(1)

    # 3. Send first task to server
    a = send_task("Go to https://scratch.mit.edu/projects/editor/?tutorial=getStarted")
    print(f"Task sent, success={a}")
    # 4. Start agent server if task succeeded
    if a:
        from browseruse.Agent.main import start_agent_server
        agent_server_process = multiprocessing.Process(target=start_agent_server)
        agent_server_process.start()
        agent_server_process.join()

    # 5. Cleanup server process
    browseruse_server_process.join()
