import socket
import pygame

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(("127.0.0.1", 5278))


    data = "來自客戶端的訊息END".encode()
    sock.sendall(data)

    data = b""
    while True:
        data += sock.recv(2)
        if b"END" in data:
            break
    print(data.decode())