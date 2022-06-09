import socket

port = 5050

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", port))

while (True):
    msg = s.recv(1024)
    print(msg.decode("utf-8"))
