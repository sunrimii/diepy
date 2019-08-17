import socketserver
import zlib
import pickle


EOF = bytes("結束", "utf-8")


class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class Handler(socketserver.BaseRequestHandler):
    def _recv_events(self):
        # 接收資料
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
        events = pickle.loads(data)
    
        return events

    def _send_drawinfo(self, drawinfo):
        # 序列化
        data = pickle.dumps(drawinfo)
        # 壓縮
        data = zlib.compress(data)
        # 加上結束標記
        data += EOF
        # 傳送資料
        self.request.sendall(data)

    def handle(self):
        events = self._recv_events()
        # 處理
        # drawinfo = ...
        self._send_drawinfo(drawinfo)


class Client:
    def __init__(self):
        