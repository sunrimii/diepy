import socket
import socketserver
import zlib
import pickle


EOF = bytes("結束", "utf-8")


class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class Handler(socketserver.BaseRequestHandler):
    def _recv(self):
        # 接收資料 可以改 玩家斷線
        data = b""
        while True:
            data += self.request.recv(1024)
            if data[-6:] == EOF:
                break
        # 移除結束標記
        data = data[:-6]
        # 解壓縮
        data = zlib.decompress(data)
        # 反序列化
        data = pickle.loads(data)

        return data

    def _sendall(self, data):
        # 序列化
        data = pickle.dumps(data)
        # 壓縮
        data = zlib.compress(data)
        # 加上結束標記
        data += EOF
        # 傳送資料
        self.request.sendall(data)

    def handle(self):
        data = self._recv()
        # 處理
        # drawinfo = ...
        self._sendall(data)


class Client:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port


def Server():