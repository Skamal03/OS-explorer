import socket
import json
import threading
from main import Kernel

class OSServer:
    def __init__(self, host="localhost", port=9999):  # Changed to 0.0.0.0
        self.kernel = Kernel()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        print(f"Server started on {host}:{port}")

    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(1024).decode()
            request = json.loads(data)
            response = {"status": "error", "message": "Invalid request"}

            if request.get("action") == "create_process":
                try:
                    proc = self.kernel.create_process(
                        request["name"],
                        request["priority"],
                        request["burst"],
                        request["arrival"]
                    )
                    print(f"Process created: PID={proc.pid}, Name={proc.name}, State={proc.state}")
                    response = {"status": "success", "pid": proc.pid}
                except Exception as e:
                    response = {"status": "error", "message": str(e)}
            elif request.get("action") == "list_processes":  # Added action
                processes = self.kernel.list_all_processes()
                response = {
                    "status": "success",
                    "processes": [
                        {"pid": p.pid, "name": p.name, "state": p.state}
                        for p in processes
                    ]
                }

            client_socket.send(json.dumps(response).encode())
        except Exception as e:
            print(f"Error handling client: {e}")
            response = {"status": "error", "message": str(e)}
            client_socket.send(json.dumps(response).encode())
        finally:
            client_socket.close()

    def run(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Connection from {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

if __name__ == "__main__":
    server = OSServer()
    server.run()