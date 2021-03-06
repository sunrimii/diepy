import pickle
import socket
import socketserver
import time
import zlib


EOF = bytes("結束", "utf-8")


class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, game):
        super().__init__(server_address, RequestHandlerClass)

        self.game = game
        self.game.init_server()
        self.game.add_tank(self.server_address, serverself=True)

        self.maxnum_of_tanks = 4

        self.events = {}
        
    # def server_activate(self):
    #     self.socket.listen(self.request_queue_size)
    
    # def service_actions(self):
    #     pass

class Handler(socketserver.BaseRequestHandler):
    def recv_(self):
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
        data = pickle.loads(data)

        return data

    def sendall_(self, data):
        # 序列化
        data = pickle.dumps(data)
        # 壓縮
        data = zlib.compress(data)
        # 加上結束標記
        data += EOF
        # 傳送資料
        self.request.sendall(data)

    def handle(self):
        is_verified = False

        # 分支伺服器循環
        while True:
            # 等待客戶端傳來輸入事件
            event = self.recv_()
            self.server.events[self.client_address] = event

            # 第一次循環驗證客戶端身分
            if not is_verified:
                # 檢查輸入事件是否符合格式
                if isinstance(event, tuple) and len(event) == 3:
                    self.server.game.add_tank(self.client_address)
                    is_verified = True

                # 驗證失敗
                else:
                    del self.server.events[self.client_address]
                    raise Exception

            # 等待伺服器處理完遊戲邏輯
            while self.server.events:
                time.sleep(0.01)

            # 傳送 精靈們 和 其能力值面板 和 其鏡頭位置 給客戶端
            data = (self.server.sprites, self.server.skill_panels[self.client_address], 
                self.server.cams[self.client_address],)
            self.sendall_(data)

            # 刪除鏡頭位置使伺服器判斷是否已傳送
            del self.server.cams[self.client_address]

class Client:
    def __init__(self, addr, game):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(addr)

        self.game = game

        self.sprites = ()
        self.skill_panel = ()
        self.cam = ()
        
    def __enter__(self):
        return self

    def __exit__(self, *arg):
        self.sock.close()

    def recv_(self):
        # 接收資料
        data = b""
        while True:
            data += self.sock.recv(1024)
            if data[-6:] == EOF:
                break
        # 移除結束標記
        data = data[:-6]
        # 解壓縮
        data = zlib.decompress(data)
        # 反序列化
        data = pickle.loads(data)

        return data

    def sendall_(self, data):
        # 序列化
        data = pickle.dumps(data)
        # 壓縮
        data = zlib.compress(data)
        # 加上結束標記
        data += EOF
        # 傳送資料
        self.sock.sendall(data)
