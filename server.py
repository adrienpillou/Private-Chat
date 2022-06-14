import socket
import threading
from os import path
from client import BUFFER_SIZE
from database import *
from rich import print
import pickle

PORT = 9999
SERVER_ADDRESS = socket.gethostbyname(socket.gethostname())
HEADER = 64
FORMAT = "utf-8"
BUFFER_SIZE = 512
HEADER_SIZE = 8

ip_lookup = dict()
connections = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_ADDRESS, PORT))

def get_time():
    return time.strftime("%H:%M")

def send_connected_users(connection):
    users = dict()
    for i, c in enumerate(connections):
        client_ip = c.getpeername()[0]
        if(client_ip in ip_lookup.keys()):
            users[i] = ip_lookup[client_ip]
    
    message = f"{len(users.keys())} user(s) is currently connected to this room:"
    for k in users.keys():
        message += f"\n- {users[k]}"
    
    send_message(connection, message)
    
    # Sending an object with pickle
    #o = pickle.dumps(users)
    #message = bytes( f"{len(o)}/PICK".ljust(HEADER_SIZE), FORMAT) + o
    #connection.send(message)

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
        header = connection.recv(HEADER_SIZE).decode(FORMAT)
        message_type = header.split("/")[1]
        message_length = int(header.split("/")[0])
        message = connection.recv(message_length).decode(FORMAT)

        if(message == "!quit"):
            print(f"[yellow]User {client_username} asked to disconnect.")
            broadcast_message_all(f"{client_username} left the room.")
            connected = False
        elif(message == "!users"):
            send_connected_users(connection)
            print(f"[yellow]List of connected users submitted to {client_username}.")
        else:
            add_message(get_user_id_by_name(client_username), message)
            broadcast_message(f"[{get_time()}] {client_username} > {message}", connection)
        
    connection.close()
    connections.remove(connection)

def encapsulate(message, message_type):
    # 'TEXT' => textual message
    header = str(len(message)) + "/" + message_type
    encapsulated = f"{header:<{HEADER_SIZE}}" + message
    return encapsulated

def send_message(connection, message):
    message = encapsulate(message, "TEXT")
    connection.send(bytes(message, FORMAT))
    
def authenticate_client(username, password, connection):
    if(not user_exists(username)):
        add_user(username, password)
        send_message(connection, "!ACCEPTED")
        return True

    user_id = get_user_id_by_name(username)
    encrypted_password = get_user_password(user_id)
    db_password = decrypt(encrypted_password.encode())

    if db_password == password:
        send_message(connection, "!ACCEPTED")
        return True

    elif db_password != password:
        send_message(connection, "!DECLINED")
        return False

def broadcast_message(message, connection):
    for c in connections:
        if (c != connection):
            send_message(c, message)
    print("[BROADCAST] "+message)

def broadcast_message_all(message):
    for c in connections:
        send_message(c, message)
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