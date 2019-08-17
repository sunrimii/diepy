import socket


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(("localhost", 5278))
    
    while True:
        data = input(">>  ")
        sock.sendall(bytes(data, "utf-8"))
        print("send ok")

        data = str(sock.recv(5), "utf-8")
        print(f">>  {data}")
