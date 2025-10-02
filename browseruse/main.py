import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from browseruse.tools.browserUseClient import send_task
from browseruse.tools.browserUseServer import start_server
import threading
import multiprocessing



if __name__ == "__main__":

        
        browseruse_server_process = multiprocessing.Process(target=start_server)
        browseruse_server_process.start()
        while True:
                a= send_task("Go to https://scratch.mit.edu/projects/editor/?tutorial=getStarted")
                if a:
                        
                        from browseruse.Agent.main import start_agent_server
                        agent_server_process = multiprocessing.Process(target=start_agent_server)
                        agent_server_process.start()
                        break
                        
                time.sleep(2)
        time.sleep(2)  # Ensure the browseruse server starts before the agent server
        
        agent_server_process.join()
        # start_server()
