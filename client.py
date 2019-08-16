import socket
from core import Game


if __name__ == "__main__":
    game = Game()
    game.init_client()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("59.127.31.13", 5278))
        print("已連線至伺服器")
        EOF = b"\xe7\xb5\x90\xe6\x9d\x9f"
        while game.is_running:
            data = b""
            while True:
                data += s.recv(1024)
                if data[-6:] == EOF:
                    break
            data = data[:-6]
                
            game.parse_screen_data(data)

            data = game.get_event()
            data += EOF
            s.send(data)
