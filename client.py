import socket
import pickle

import pygame

from config import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1" , 5278))
print("已連線至遊戲伺服器")

pygame.init()
pygame.display.set_caption("Diepy")
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((1920,1080))

# 建立地圖
world = pygame.Surface((2000, 2000))
# 填充背景
world.fill(COLOR_OF_BG)
# 繪製減速區
world_w, world_h = world.get_size()
pygame.gfxdraw.box(world, (0,0,world_w,300), COLOR_OF_SLOWZONE)
pygame.gfxdraw.box(world, (0,0,300,world_h), COLOR_OF_SLOWZONE)
pygame.gfxdraw.box(world, (0,world_h-300,world_w,300), COLOR_OF_SLOWZONE)
pygame.gfxdraw.box(world, (world_w-300,0,300,world_h), COLOR_OF_SLOWZONE)
# 繪製網格
for x in range(0, world_w, 20):
    pygame.gfxdraw.box(world, (x,0,2,world_h), COLOR_OF_GRID)
for y in range(0, world_h, 20):
    pygame.gfxdraw.box(world, (0,y,world_w,2), COLOR_OF_GRID)

bg = world.copy()

cam = pygame.Rect(0, 0, 1920, 1080)
# cam.center = tank.pos

while True:
    # pressed_keys = pickle.dumps(pygame.key.get_pressed())
    # s.sendall(pressed_keys)
    # is_click = pickle.dumps(pygame.mouse.get_pressed()[0])
    # s.sendall(is_click)
    # mouse_pos = pickle.dumps(pygame.mouse.get_pos())
    # s.sendall(mouse_pos)
    data = pickle.dumps((pygame.key.get_pressed(), pygame.mouse.get_pressed()[0], pygame.mouse.get_pos()))
    s.sendall(data)
    print("已傳送玩家指令")

    data = b""
    while True:
        packet = s.recv(1024)
        if not packet:
            break
        data += packet
    print("已收到伺服器回應")

    # 更新畫面
    enemies, bullet_packs, players = pickle.loads(data)
    enemies.clear(world, bg)
    bullet_packs.clear(world, bg)
    players.clear(world, bg)
    enemies.draw(world)
    bullet_packs.draw(world)
    players.draw(world)
    
    # 使鏡頭平滑移動
    cam.center += (tank.pos-cam.center) * 0.1

    # 限制移動邊界
    cam.x = min(max(cam.x, 0), world_w-cam.w) 
    cam.y = min(max(cam.y, 0), world_h-cam.h)

    # 建立要顯示給玩家的畫面
    player_scr = world.subsurface(cam)
    
    # 於右下角顯示剩餘子彈數
    text = "x" + str(tank.num_of_bullets)
    font = pygame.font.SysFont("impact", 40)
    font_surf = font.render(text, True, BLACK)
    x = 1700
    y = 500
    player_scr.blit(font_surf, (x,y))
    font_surf = font.render(text, True, WHITE)
    x -= 3
    y -= 3
    player_scr.blit(font_surf, (x,y))

            
    

    # 更新畫面
    screen.blit(player_scr, (0,0))
    pygame.display.update()