import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 65432

def send_task(task, client_id):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(task.encode("utf-8"))
            data = s.recv(1024)
        print(f"Client {client_id}: ✅ {data.decode().strip()}")
    except Exception as e:
        print(f"Client {client_id}: ❌ {e}")

def run_load_test(num_clients=10):
    threads = []
    start = time.time()

    send_task("Go to https://scratch.mit.edu/projects/editor/?tutorial=getStarted",1)
    time.sleep(5)  
    for i in range(num_clients):
        t = threading.Thread(target=send_task, args=(f"refresh", i))
        threads.append(t)
        t.start()
        time.sleep(0.1)  # small delay between clients

    for t in threads:
        t.join()

    print(f"\n⏱️ Completed {num_clients} tasks in {time.time()-start:.2f}s")

if __name__ == "__main__":
    run_load_test(50)  # Try 20 parallel connections
