# agent_client.py
import socket

def send_task(task: str):
    host = "127.0.0.1"
    port = 65432
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(task.encode("utf-8"))
        response = s.recv(1024)
        print("📨 Server response:", response.decode("utf-8"))


if __name__ == "__main__":
    send_task("Go to scratch.mit.edu")
    # send_task("Go to geeksforgeeks.org")
    # send_task("exit")   # gracefully shut down worker
