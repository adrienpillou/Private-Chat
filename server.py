import socket
import threading
from os import path
from database import *
from rich import print

PORT = 9999
SERVER_ADDRESS = socket.gethostbyname(socket.gethostname())
HEADER = 64
FORMAT = "utf-8"
BUFFER_SIZE = 512

ip_lookup = dict()
connections = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_ADDRESS, PORT))

def get_time():
    return time.strftime("%H:%M")

def handle_client(connection, address):
    ip_address = address[0]
    connected = False
    while not connected:
        packet = connection.recv(128).decode(FORMAT)
        (client_username, client_password) = packet.split("/")
        ip_lookup[ip_address] = client_username
        connected = authenticate_client(client_username, client_password, connection)

    if(connected):
        print(f"New connection: {ip_address} connected as {client_username}.")
        broadcast_message_all(f"[{get_time()}] [blue]{client_username}[/blue] has joined the room.")

    while connected:
        message = connection.recv(BUFFER_SIZE).decode(FORMAT)
        add_message(get_user_id_by_name(client_username), message)
        broadcast_message(f"[{get_time()}] {client_username} > {message}", connection)
        if(message == "!disconnect"):
            connected = False
    connection.close()
    connections.remove(connection)
    

def authenticate_client(username, password, connection):
    if(not user_exists(username)):
        add_user(username, password)
        connection.send(bytes("!ACCEPTED", FORMAT))
        return True

    user_id = get_user_id_by_name(username)
    db_password = get_user_password(user_id)

    if db_password == password:
        connection.send(bytes("!ACCEPTED", FORMAT))
        return True
    elif db_password != password:
        connection.send(bytes("!DECLINED", FORMAT))
        return False

def broadcast_message(message, connection):
    for c in connections:
        if (c != connection):
            c.send(bytes(message, FORMAT))
    print("[BROADCAST] "+message)

def broadcast_message_all(message):
    for c in connections:
        c.send(bytes(message, FORMAT))
    print("[ALL] "+message)

def start():
    server.listen()
    print(f"Server is listening on {SERVER_ADDRESS}:{PORT}")
    create_database()
    while True:
        connection, address = server.accept()
        connections.append(connection)
        thread = threading.Thread(target=handle_client, args=(connection, address))
        thread.start()
        print(f"Active connections: {threading.activeCount()-1}")

def splash():
    print("[cyan] _____      _            _          _____ _           _   ")
    print("[cyan]|  __ \    (_)          | |        / ____| |         | |  ")
    print("[cyan]| |__) | __ ___   ____ _| |_ ___  | |    | |__   __ _| |_ ")
    print("[cyan]|  ___/ '__| \ \ / / _` | __/ _ \ | |    | '_ \ / _` | __|")
    print("[cyan]| |   | |  | |\ V / (_| | ||  __/ | |____| | | | (_| | |_ ")
    print("[cyan]|_|   |_|  |_| \_/ \__,_|\__\___|  \_____|_| |_|\__,_|\__|")
    print("[green]Server test version.[/green] Type alt+f4 to quit.")
    print("\n")

def stop():
    server.close()

splash()
print("Private Chat server up and running...")
start()