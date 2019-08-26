from core import Diepy


if __name__ == "__main__":
    diepy = Diepy()
    diepy.load_materials()
    diepy.select_mode()

    if diepy.mode == "single":
        diepy.add_tank()
        diepy.add_mothership()
        while diepy.is_running:
            diepy.add_cross()
            event = diepy.get_event()
            diepy.run_logic(event)
            diepy.update_screen()

    elif diepy.mode == "server":
        import threading
        import time

        from network import Server, Handler


        host = "127.0.0.1"
        port = 5278
        with Server((host, port), Handler, diepy) as server:
            # 每有一客戶端連入就啟動一分支伺服器
            server_thread = threading.Thread(target=server.serve_forever)
            # server_thread.daemon = True # 主執行緒關閉時也關閉其他所有執行緒
            server_thread.start()

            # 
            while len(server.game.tanks) < 2:
                time.sleep(0.01)
            
            diepy.add_mothership()
            
            # 伺服器循環
            while diepy.is_running:
                # 伺服器自己傳送輸入事件
                server.events[server.server_address] = diepy.get_event()

                # 等待客戶端傳來輸入事件
                while len(server.events) is not len(server.game.tanks):
                    time.sleep(0.01)
                    
                # 處理遊戲邏輯
                diepy.add_cross()
                diepy.run_logic(server.events)
                server.sprites = diepy.get_sprites()
                server.skill_panels = diepy.get_skill_panels()
                server.cams = diepy.get_cams()

                # 清空輸入事件使伺服器分支判斷伺服器是否處理完遊戲邏輯
                server.events.clear()

                # 等待 精靈們 和其 其能力值面板 和 鏡頭位置 傳送客戶端
                while len(server.cams) > 1:
                    time.sleep(0.01)
                
                # 伺服器自己更新螢幕
                diepy.update_screen()

            server.shutdown()
    
    elif diepy.mode == "client":
        import time

        from network import Client


        host = "127.0.0.1"
        port = 5278
        with Client((host, port)) as client:
            # 客戶端主循環
            while diepy.is_running:
                # 傳送輸入事件給分支伺服器
                event = diepy.get_event()
                client.sendall_(event)

                # 等待分支伺服器傳來繪製位置和鏡頭位置
                sprites, skill_panel, cam = client.recv_()

                diepy.update_screen(sprites, skill_panel, cam)
