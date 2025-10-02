# agent_client.py
import socket
import time

def send_task(task: str):
    ''' User can do action on website like button press, scrolling, 
    searching, filling text boxes, navigating to another site 
    but cannot do drag and drop like actions. '''

    host = "127.0.0.1"
    port = 65432
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall(task.encode("utf-8"))
                response = s.recv(1024)
                print("📨 Server response:", response.decode("utf-8"))
            return True
              
        except Exception as e:
            print("❌ Error occurred:", e)
            time.sleep(2)  
            continue


# if __name__ == "__main__":
   
#     send_task("Go to https://scratch.mit.edu/projects/editor/?tutorial=getStarted")
#     # send_task("refresh")   # gracefully shut down worker
    # send_task("go to operators do not open new tab")
    # send_task("exit")   # gracefully shut down worker