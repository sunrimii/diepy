from core import Game


if __name__ == "__main__":
    game = Game()
    game.init_server()
    game.load_material()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("192.168.1.100", 5278))
        s.listen(1)

        conn, addr = s.accept()
        addr = str(addr)
        print("收到來自", addr, "的連線")
        game.add_player(addr)
        EOF = b"\xe7\xb5\x90\xe6\x9d\x9f"
        with conn:
            while True:
                game.run_logic()
                data = game.get_screen_data(addr)
                data += EOF
                conn.sendall(data)

                data = b""
                while True:
                    data += conn.recv(1024)
                    if data[-6:] == EOF:
                        break
                data = data[:-6]
                game.handle_event(addr, data)