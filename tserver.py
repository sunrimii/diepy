import socketserver

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            self.data = self.request.recv(5)
            print("recv ok")
            self.request.sendall(self.data)
            print("send ok")

with socketserver.TCPServer(("localhost", 5278), Handler) as server:
    server.serve_forever()