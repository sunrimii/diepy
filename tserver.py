import socket
import pygame


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(("127.0.0.1", 5278))
    sock.listen(1)
    conn, addr = sock.accept()
    with conn:



        data = b""
        while True:
            data += conn.recv(2)
            if b"END" in data:
                break
        print(data.decode())


        data = "來自伺服器的訊息END".encode()
        conn.sendall(data)
