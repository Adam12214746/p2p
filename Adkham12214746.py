import socket
import threading
import os
import json
import csv
from PIL import Image

SERVER_IP = '127.0.0.1'  # Replace with your server IP address
SERVER_PORT = 8000  # Replace with your desired server port number
MAX_CONNECTIONS = 10

connected_clients = []

def display_menu():
    print("1. Send and visualize an image")
    print("2. Send and visualize a CSV file")
    print("3. Send and visualize a JSON file")
    print("4. Broadcast a file")
    print("5. Exit")

    choice = input("Enter your choice: ")
    return int(choice)

def send_file(client_socket, file_path):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    client_socket.sendall(file_name.encode())
    client_socket.sendall(str(file_size).encode())

    with open(file_path, 'rb') as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            client_socket.sendall(data)

def receive_file(client_socket):
    file_name = client_socket.recv(1024).decode()
    file_size = int(client_socket.recv(1024).decode())

    with open(file_name, 'wb') as file:
        received_bytes = 0
        while received_bytes < file_size:
            data = client_socket.recv(1024)
            received_bytes += len(data)
            file.write(data)

def handle_client(client_socket):
    connected_clients.append(client_socket)

    choice = display_menu()

    if choice == 1:
        receive_file(client_socket)

        image = Image.open("received_image.jpg")
        image.show()

    elif choice == 2:
        receive_file(client_socket)

        with open("received_data.csv", 'r') as file:
            csv_data = csv.reader(file)
            for row in csv_data:
                print(row)

    elif choice == 3:
        receive_file(client_socket)

        with open("received_data.json", 'r') as file:
            json_data = json.load(file)
            print(json_data)

    elif choice == 4:
        file_path = input("Enter the path of the file to broadcast: ")
        files_to_send = []

        for client in connected_clients:
            files_to_send.append((client, file_path))

        for client, file_path in files_to_send:
            threading.Thread(target=send_file, args=(client, file_path)).start()

    client_socket.close()
    connected_clients.remove(client_socket)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(MAX_CONNECTIONS)
    print("Server started on {}:{}".format(SERVER_IP, SERVER_PORT))

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt:
        server_socket.close()
        print("Server stopped.")

if __name__ == '__main__':
    start_server()