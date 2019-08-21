import os

import pygame
import pygame.gfxdraw
import pygame.freetype
import numpy as np


SIZE_OF_BATTLEFIELD = 5000
SIZE_OF_SLOWZONE = 300
SIZE_OF_TANK = 140
SIZE_OF_BULLET = 35
SIZE_OF_MOTHERSHIP = 350

COLOR_OF_BATTLEFIELD = (205, 205, 205)
COLOR_OF_GRID = (215, 215, 215)
COLOR_OF_SLOWZONE = (210, 210, 210)
COLOR_OF_HP = (100, 200, 100)
COLOR_OF_MOTHERSHIP = (100, 200, 100)

BLACK = (0, 0, 0)

GRAY = (153, 153, 153)
RED = (241, 78, 84)
YELLOW = (255, 232, 105)
GREEN = (0, 255, 110)
BLUE = (0, 178, 255)
PURPLE = (191, 127, 245)
BROWN = (150, 94, 63)

DARK_GRAY = (114, 114, 114)
DARK_RED = (180, 58, 63)
DARK_YELLOW = (191, 174, 78)
DARK_GREEN = (10, 168, 82)
DARK_BLUE = (0, 133, 168)
DARK_PURPLE = (143, 95, 183)
DARK_BROWN = (99, 62, 41)


def draw_battlefield():
    battlefield = pygame.Surface((SIZE_OF_BATTLEFIELD, SIZE_OF_BATTLEFIELD))
    battlefield.fill(COLOR_OF_SLOWZONE)
    
    rect = (SIZE_OF_SLOWZONE, SIZE_OF_SLOWZONE, SIZE_OF_BATTLEFIELD-2*SIZE_OF_SLOWZONE, SIZE_OF_BATTLEFIELD-2*SIZE_OF_SLOWZONE)
    pygame.gfxdraw.box(battlefield, rect, COLOR_OF_BATTLEFIELD)

    # 網格
    for x in range(0, SIZE_OF_BATTLEFIELD, 25):
        pygame.gfxdraw.box(battlefield, (x,0,2,SIZE_OF_BATTLEFIELD), COLOR_OF_GRID)
    for y in range(0, SIZE_OF_BATTLEFIELD, 25):
        pygame.gfxdraw.box(battlefield, (0,y,SIZE_OF_BATTLEFIELD,2), COLOR_OF_GRID)

    pygame.image.save(battlefield, "material/battlefield.png")

def draw_tank_and_bullet():
    for color, body_color, border_color in (("blue",BLUE,DARK_BLUE), ("purple",PURPLE,DARK_PURPLE), ("red",RED,DARK_RED), ("green",GREEN,DARK_GREEN)):
        for scale_of_barrel in np.arange(1.0, 0.8, -0.04):
            scale_of_barrel = round(scale_of_barrel, 2)

            tank = pygame.Surface((SIZE_OF_TANK, SIZE_OF_TANK))
            
            border = SIZE_OF_TANK // 25
            
            # 坦克砲管
            # 砲管以水平開口朝右繪製 再根據滑鼠旋轉
            # x,y--------w----------
            # |                    |
            # h                    h
            # |                    |
            # -----------w----------
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
            pygame.gfxdraw.filled_circle(tank, x, y, r, border_color)
            r -= border
            pygame.gfxdraw.filled_circle(tank, x, y, r, body_color)

            pygame.image.save(tank, f"material/{color}-tank-{scale_of_barrel}.png")

        # 子彈
        bullet = pygame.Surface((SIZE_OF_BULLET, SIZE_OF_BULLET))
        x = SIZE_OF_BULLET // 2
        y = SIZE_OF_BULLET // 2
        r = x
        pygame.gfxdraw.filled_circle(bullet, x, y, r, border_color)
        border = SIZE_OF_BULLET // 7
        r -= border
        pygame.gfxdraw.filled_circle(bullet, x, y, r, body_color)

        pygame.image.save(bullet, f"material/{color}-bullet.png")

def draw_mothership():
    num_of_edge = 12
    
    border = SIZE_OF_MOTHERSHIP / 50

    angle = 360 / num_of_edge
    angle_offset = angle / 2

    center = (SIZE_OF_MOTHERSHIP / 2, SIZE_OF_MOTHERSHIP / 2)

    for scale_of_barrel in np.arange(1.0, 0.8, -0.04):
        mothership = pygame.Surface((SIZE_OF_MOTHERSHIP, SIZE_OF_MOTHERSHIP))

        # 母艦砲管
        scale_of_barrel = round(scale_of_barrel, 2)
        w = SIZE_OF_MOTHERSHIP / 2.2 * scale_of_barrel * 1.08
        h = SIZE_OF_MOTHERSHIP / num_of_edge * 2
        x = 0
        y = -h / 2

        for color, x, y, w, h in ((DARK_GRAY, x, y, w, h), (GRAY, x, y+border, w-border*0.8, h-2*border)):
            p1 = pygame.math.Vector2(x, y)
            p2 = p1 + (0, h)
            p3 = p2 + (w, 0)
            p4 = p3 - (0, h)

            p1.rotate_ip(angle_offset)
            p2.rotate_ip(angle_offset)
            p3.rotate_ip(angle_offset)
            p4.rotate_ip(angle_offset)

            for _ in range(num_of_edge):
                p1.rotate_ip(angle)
                p2.rotate_ip(angle)
                p3.rotate_ip(angle)
                p4.rotate_ip(angle)
                pnts = [p1+center, p2+center, p3+center, p4+center]

                pygame.gfxdraw.filled_polygon(mothership, pnts, color)

        # 母艦本體
        outerbody_len = pygame.math.Vector2(SIZE_OF_MOTHERSHIP / 2.5, 0)
        innerbody_len = outerbody_len - (border, 0)

        outerbody = []
        innerbody = []

        for _ in range(num_of_edge):
            outerbody_len.rotate_ip(angle)
            innerbody_len.rotate_ip(angle)

            outerbody.append(outerbody_len + center)
            innerbody.append(innerbody_len + center)

        pygame.gfxdraw.filled_polygon(mothership, outerbody, DARK_BROWN)
        pygame.gfxdraw.filled_polygon(mothership, innerbody, BROWN)

        pygame.image.save(mothership, f"material/mothership-{scale_of_barrel}.png")


# 若素材不存在則產生
if not os.path.isdir("material"):
    os.mkdir("material")
    draw_battlefield()
    draw_tank_and_bullet()
    draw_mothership()


MATERIALS = {}

# 載入戰場
MATERIALS["battlefield"] = pygame.image.load("material/battlefield.png")

# 載入背景用於更新畫面
MATERIALS["background"] = MATERIALS["battlefield"].copy()

# 載入坦克和子彈
for color in ("red", "green", "blue", "purple"):
    MATERIALS[f"{color}-tank-1.0"] =  pygame.image.load(f"material/{color}-tank-1.0.png")
    MATERIALS[f"{color}-tank-0.96"] = pygame.image.load(f"material/{color}-tank-0.96.png")
    MATERIALS[f"{color}-tank-0.92"] = pygame.image.load(f"material/{color}-tank-0.92.png")
    MATERIALS[f"{color}-tank-0.88"] = pygame.image.load(f"material/{color}-tank-0.88.png")
    MATERIALS[f"{color}-tank-0.84"] = pygame.image.load(f"material/{color}-tank-0.84.png")
    MATERIALS[f"{color}-bullet"] =    pygame.image.load(f"material/{color}-bullet.png")
    
    # 將初始狀態設為透明使子彈淡入
    MATERIALS[f"{color}-bullet"].set_alpha(0)

# 將剩餘黑色設為透明
for image_key in MATERIALS:
    if image_key != "battlefield" and image_key != "background":
        MATERIALS[image_key].set_colorkey(BLACK)