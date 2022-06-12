from multiprocessing.connection import wait
from user import User
from rich import print
import socket
from getpass import getpass
import threading

CONNECTED = 1
DISCONNECTED = 2

CLIENT_STATE = DISCONNECTED

PORT = 9999
SERVER_ADDRESS = "192.168.1.70"
CLIENT_ADDRESS = socket.gethostbyname(socket.gethostname())
FORMAT = "utf-8"
BUFFER_SIZE = 512
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

current_user = None
waiting = False


def splash():
    print("[cyan] _____      _            _          _____ _           _   ")
    print("[cyan]|  __ \    (_)          | |        / ____| |         | |  ")
    print("[cyan]| |__) | __ ___   ____ _| |_ ___  | |    | |__   __ _| |_ ")
    print("[cyan]|  ___/ '__| \ \ / / _` | __/ _ \ | |    | '_ \ / _` | __|")
    print("[cyan]| |   | |  | |\ V / (_| | ||  __/ | |____| | | | (_| | |_ ")
    print("[cyan]|_|   |_|  |_| \_/ \__,_|\__\___|  \_____|_| |_|\__,_|\__|")
    print("[yellow]Client test version.[/yellow] Type ctrl+c to quit.")
    print("\n")

def authenticate():
    username = input("Username ? > ")
    password = getpass("Password ? > ")
    return User(username= username, password= password)

def connect_user():
    global CLIENT_STATE, waiting
    s.send(bytes(f"{current_user.username}/{current_user.password}", FORMAT))
    waiting = True
    
def send_message(message):
    s.send(bytes(message, FORMAT))

def disconnect_user():
    global CLIENT_STATE
    CLIENT_STATE = DISCONNECTED
    s.close()
    exit()

def parse_commands(command):
    if command=="set_password":
        password = input("Current password ? > ")
        if(current_user.password != password):
            print("[red]Wrong password")
            return
        new_password = input("New password ? > ")
        current_user.password = new_password
    if command == "quit":
        disconnect_user()

def handle_server():
    global CLIENT_STATE, waiting
    while True:
        message = s.recv(BUFFER_SIZE).decode(FORMAT)
        if len(message) > 0:
            if(CLIENT_STATE == CONNECTED):
                print(message)

            # Login responses from the server
            if(message == "!ACCEPTED" and CLIENT_STATE == DISCONNECTED):
                print("[green]Access granted to the chat room.")
                CLIENT_STATE = CONNECTED
                waiting = False
            if(message =="!DECLINED" and CLIENT_STATE == DISCONNECTED):
                print("[red]Access Declined. Please check your password.")
                CLIENT_STATE = DISCONNECTED
                waiting = False

def main():
    splash()
    global current_user, CLIENT_STATE

    s.connect((SERVER_ADDRESS, PORT))

    thread = threading.Thread(target = handle_server)
    thread.start()

    # Login phase
    while(CLIENT_STATE != CONNECTED):
        current_user = authenticate()
        connect_user()
        while waiting:
            pass
    
    while True:
        message = input()
        if message.startswith("!"):
            parse_commands(message[1::])
        if len(message) == 0:
            print("[yellow]Cannot send an empty message.")
        else:
            send_message(message)

if __name__ == "__main__":
    main()