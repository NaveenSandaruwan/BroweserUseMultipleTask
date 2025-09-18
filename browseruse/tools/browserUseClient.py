# agent_client.py
import socket

def send_task(task: str):
    ''' User can do action on website like button press, scrolling, 
    searching, filling text boxes, navigating to another site 
    but cannot do drag and drop like actions. '''

    host = "127.0.0.1"
    port = 65432
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(task.encode("utf-8"))
        response = s.recv(1024)
        print("📨 Server response:", response.decode("utf-8"))


if __name__ == "__main__":
   
    send_task("Go to https://scratch.mit.edu/projects/editor/?tutorial=getStarted")
    # send_task("refresh")   # gracefully shut down worker
    # send_task("go to operators do not open new tab")