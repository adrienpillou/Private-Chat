import socket
import threading

PORT = 9999
SERVER_ADDRESS = socket.gethostbyname(socket.gethostname())
HEADER = 64
FORMAT = "utf-8"

ip_lookup = dict()
connections = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_ADDRESS, PORT))


def handle_client(connection, address):
    ip_address = address[0]
    ip_lookup[ip_address] = connection.recv(64).decode(FORMAT)
    connected = True
    client_username = ip_lookup[ip_address]
    print(f"New connection: {ip_address} connected as {client_username}.")
    while connected:
        message = connection.recv(512).decode(FORMAT)
        print(f"{client_username} > {message}")
        broadcast_message(f"{client_username} > {message}", connection)
        if(message == "!disconnect"):
            connected = False
    connection.close()

def broadcast_message(message, connection):
    for c in connections:
        if (c != connection):
            c.send(bytes(message, FORMAT))

def start():
    server.listen()
    print(f"Server is listening on {SERVER_ADDRESS}:{PORT}")
    while True:
        connection, address = server.accept()
        connections.append(connection)
        thread = threading.Thread(target=handle_client, args=(connection, address))
        thread.start()
        print(f"Active connections: {threading.activeCount()-1}")

print("Private Chat server up and running...")
start()