import os

import pygame
import pygame.gfxdraw
import pygame.freetype
import numpy as np


SIZE_OF_BATTLEFIELD = 5000
SIZE_OF_SLOWZONE = 300
COLOR_OF_BG = (220, 220, 220)
COLOR_OF_GRID = (215, 215, 215)
COLOR_OF_SLOWZONE = (210, 210, 210)

SIZE_OF_TANK = 140
SIZE_OF_BULLET = 35
SIZE_OF_MOTHERSHIP = 350

BLACK = (0, 0, 0)
GRAY = (157, 157, 157)
DARK_GRAY = (123, 123, 123)
RED = (230, 70, 80)
DARK_RED = (190, 50, 60)
YELLOW = (255, 222, 96)
DARK_YELLOW = (190, 166, 68)
GREEN = (60, 220, 100)
DARK_GREEN = (10, 220, 50)
BLUE = (20, 180, 223)
DARK_BLUE = (20, 143, 175)

COLOR_OF_HP = (100, 200, 100)

# 若素材不存在則產生
if not os.path.isdir("material"):
    # 戰場
    battlefield = pygame.Surface((SIZE_OF_BATTLEFIELD, SIZE_OF_BATTLEFIELD))
    battlefield.fill(COLOR_OF_SLOWZONE)
    rect = (SIZE_OF_SLOWZONE, SIZE_OF_SLOWZONE, SIZE_OF_BATTLEFIELD-2*SIZE_OF_SLOWZONE, SIZE_OF_BATTLEFIELD-2*SIZE_OF_SLOWZONE)
    pygame.gfxdraw.box(battlefield, rect, COLOR_OF_BG)

    # 網格
    for x in range(0, SIZE_OF_BATTLEFIELD, 20):
        pygame.gfxdraw.box(battlefield, (x,0,2,SIZE_OF_BATTLEFIELD), COLOR_OF_GRID)
    for y in range(0, SIZE_OF_BATTLEFIELD, 20):
        pygame.gfxdraw.box(battlefield, (0,y,SIZE_OF_BATTLEFIELD,2), COLOR_OF_GRID)

    pygame.image.save(battlefield, "battlefield.png")

    for name, color_of_body, color_of_border in (("blue",BLUE,DARK_BLUE), ("yellow",YELLOW,DARK_YELLOW), ("red",RED,DARK_RED), ("green",GREEN,DARK_GREEN)):
        for scale_of_barrel in np.arange(1.0, 0.8, -0.04):
            tank = pygame.Surface((SIZE_OF_TANK, SIZE_OF_TANK))
            border = SIZE_OF_TANK // 100 * 3
            
            # 坦克砲管
            # 砲管以水平開口朝右繪製 再根據滑鼠旋轉
            # x,y--------w----------
            # |                    |
            # h                    h
            # |                    |
            # -----------w----------
            # 數字代表砲管長度
            w = SIZE_OF_TANK * scale_of_barrel // 2
            h = SIZE_OF_TANK // 5
            x = SIZE_OF_TANK // 2
            y = (SIZE_OF_TANK - h) // 2
            pygame.gfxdraw.box(tank, (x,y,w,h), DARK_GRAY)
            x += border
            y += border
            w -= border*2
            h -= border*2
            pygame.gfxdraw.box(tank, (x,y,w,h), GRAY)

            # 坦克本體
            x = SIZE_OF_TANK // 2
            y = SIZE_OF_TANK // 2
            r = SIZE_OF_TANK // 4
            pygame.gfxdraw.filled_circle(tank, x, y, r, color_of_border)
            r -= border
            pygame.gfxdraw.filled_circle(tank, x, y, r, color_of_body)

            scale_of_barrel = round(scale_of_barrel, 2)
            pygame.image.save(tank, f"material/{name}-tank-{scale_of_barrel}.png")

        # 子彈
        bullet = pygame.Surface((SIZE_OF_BULLET, SIZE_OF_BULLET))
        x = SIZE_OF_BULLET // 2
        y = SIZE_OF_BULLET // 2
        r = x
        pygame.gfxdraw.filled_circle(bullet, x, y, r, color_of_border)
        border = 3
        r -= border
        pygame.gfxdraw.filled_circle(bullet, x, y, r, color_of_body)

        pygame.image.save(bullet, f"material/{name}-bullet.png")

    # 母艦砲管
    mothership = pygame.Surface((SIZE_OF_MOTHERSHIP, SIZE_OF_MOTHERSHIP))
    w = SIZE_OF_MOTHERSHIP // 3
    h = SIZE_OF_MOTHERSHIP // 10
    x = SIZE_OF_MOTHERSHIP // 2
    y = (SIZE_OF_MOTHERSHIP - h) // 2
    pygame.gfxdraw.box(mothership, (x,y,w,h), DARK_GRAY)
        
    # 母艦本體
    x = SIZE_OF_MOTHERSHIP // 2
    y = SIZE_OF_MOTHERSHIP // 2
    r = SIZE_OF_MOTHERSHIP // 4
    pygame.gfxdraw.filled_circle(mothership, x, y, r, DARK_GRAY)
    border = SIZE_OF_MOTHERSHIP // 30
    r -= border
    pygame.gfxdraw.filled_circle(mothership, x, y, r, GRAY)

    pygame.image.save(mothership, f"material/mothership.png")

MATERIALS = {}

# 載入戰場
MATERIALS["battlefield"] = pygame.image.load("material/battlefield.png")

# 載入背景用於更新畫面
MATERIALS["background"] = MATERIALS["battlefield"].copy()

# 載入坦克
MATERIALS["red-tank-1.0"] =  pygame.image.load(f"material/red-tank-1.0.png")
MATERIALS["red-tank-0.96"] = pygame.image.load(f"material/red-tank-0.96.png")
MATERIALS["red-tank-0.92"] = pygame.image.load(f"material/red-tank-0.92.png")
MATERIALS["red-tank-0.88"] = pygame.image.load(f"material/red-tank-0.88.png")
MATERIALS["red-tank-0.84"] = pygame.image.load(f"material/red-tank-0.84.png")
MATERIALS["yellow-tank-1.0"] =  pygame.image.load(f"material/yellow-tank-1.0.png")
MATERIALS["yellow-tank-0.96"] = pygame.image.load(f"material/yellow-tank-0.96.png")
MATERIALS["yellow-tank-0.92"] = pygame.image.load(f"material/yellow-tank-0.92.png")
MATERIALS["yellow-tank-0.88"] = pygame.image.load(f"material/yellow-tank-0.88.png")
MATERIALS["yellow-tank-0.84"] = pygame.image.load(f"material/yellow-tank-0.84.png")
MATERIALS["green-tank-1.0"] =  pygame.image.load(f"material/green-tank-1.0.png")
MATERIALS["green-tank-0.96"] = pygame.image.load(f"material/green-tank-0.96.png")
MATERIALS["green-tank-0.92"] = pygame.image.load(f"material/green-tank-0.92.png")
MATERIALS["green-tank-0.88"] = pygame.image.load(f"material/green-tank-0.88.png")
MATERIALS["green-tank-0.84"] = pygame.image.load(f"material/green-tank-0.84.png")
MATERIALS["blue-tank-1.0"] =  pygame.image.load(f"material/blue-tank-1.0.png")
MATERIALS["blue-tank-0.96"] = pygame.image.load(f"material/blue-tank-0.96.png")
MATERIALS["blue-tank-0.92"] = pygame.image.load(f"material/blue-tank-0.92.png")
MATERIALS["blue-tank-0.88"] = pygame.image.load(f"material/blue-tank-0.88.png")
MATERIALS["blue-tank-0.84"] = pygame.image.load(f"material/blue-tank-0.84.png")

# 載入子彈
MATERIALS["red-bullet"] =    pygame.image.load(f"material/red-bullet.png")
MATERIALS["yellow-bullet"] = pygame.image.load(f"material/yellow-bullet.png")
MATERIALS["green-bullet"] =  pygame.image.load(f"material/green-bullet.png")
MATERIALS["blue-bullet"] =   pygame.image.load(f"material/blue-bullet.png")
