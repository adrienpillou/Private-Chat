from user import User
from rich import print
import socket
from getpass import getpass
import threading

PORT = 9999
SERVER_ADDRESS = "192.168.1.70"
CLIENT_ADDRESS = socket.gethostbyname(socket.gethostname())
FORMAT = "utf-8"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

current_user = None

db = dict()
db["Adrien"] = "1234"

def splash():
    print("[cyan] _____      _            _          _____ _           _   ")
    print("[cyan]|  __ \    (_)          | |        / ____| |         | |  ")
    print("[cyan]| |__) | __ ___   ____ _| |_ ___  | |    | |__   __ _| |_ ")
    print("[cyan]|  ___/ '__| \ \ / / _` | __/ _ \ | |    | '_ \ / _` | __|")
    print("[cyan]| |   | |  | |\ V / (_| | ||  __/ | |____| | | | (_| | |_ ")
    print("[cyan]|_|   |_|  |_| \_/ \__,_|\__\___|  \_____|_| |_|\__,_|\__|")
    print("[yellow]Test version.[/yellow] Type ctrl+c to quit.")
    print("\n")


def auth():
    username = input("Username ? > ")
    if (username not in db.keys()):
        password = getpass("Set your password > ")
        confirm = getpass("Confirm your password > ")
        if(confirm == password):
            db[username] = password
        else:
            print("[yellow]Passwords doesn't match.")
            return
        print("[yellow]Account created.")
    else:
        password = getpass("Password ? > ")
        if (password != db[username]):
            print("[red]Connection error: wrong password.")
            return
    return User(username= username, password= password)

def connect_user():
    s.connect((SERVER_ADDRESS, PORT))
    s.send(bytes(current_user.username, FORMAT))
    print("[green]Connection established.")
    
def send_message(message):
    s.send(bytes(message, "utf-8"))

def parse_commands(command):
    if command=="set_password":
        password = input("Current password > ")
        if(current_user.password != password):
            print("[red]Wrong password")
            return
        new_password = input("New password > ")
        current_user.password = new_password
    if command == "quit":
        disconnect_user()

def handle_server():
    while True:
        message = s.recv(512).decode(FORMAT)
        if len(message) > 0:
            print(message)

def disconnect_user():
    s.close()
    exit()

def main():
    splash()
    global current_user
    while(current_user is None):
        current_user = auth()
        connect_user()
    thread = threading.Thread(target = handle_server)
    thread.start()
    while True:
        message = input(f"> ")
        if message.startswith("!"):
            parse_commands(message[1::])
        if len(message) == 0:
            print("[yellow]Cannot send an empty message.")
        else:
            send_message(message)

if __name__ == "__main__":
    main()