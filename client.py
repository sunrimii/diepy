import socket
import pickle

import pygame
import pygame.gfxdraw

from config import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
s.connect(("127.0.0.1" , 5278))
print("已連線至遊戲伺服器")




while True:
    command = pygame.key.get_pressed(), pygame.mouse.get_pressed()[0], pygame.mouse.get_pos()
    data = pickle.dumps(command)
    s.sendall(data)
    print("已傳送玩家指令")

    data = b""

    while True:
        packet = b""
        try:
            packet = s.recv(4096)
        except:
            pass
        if packet == b"":
            break
        data += packet
        print(packet)
    print("已收到伺服器回應")

    data = pickle.loads(data)
    player_scr = pygame.surfarray.make_surface(data)
    screen.blit(player_scr, (0,0))
    pygame.display.update()
    print("畫面已更新")
    
    # 從群組中找出坦克
    # tank = None
    # for _ in player:
    #     if hasattr(_, "recoil"):
    #         tank = _
    #         break

    

            
    
