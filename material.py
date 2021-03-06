import os

import pygame
import pygame.gfxdraw


SIZE_OF_BATTLEFIELD = 5000
SIZE_OF_SLOWZONE = 300
SIZE_OF_TANK = 140
SIZE_OF_BULLET = 35
SIZE_OF_MOTHERSHIP = 350
SIZE_OF_LITTLESHIP = 40
SIZE_OF_CROSS = 60

COLOR_OF_BATTLEFIELD = (210, 210, 210)
COLOR_OF_GRID = (215, 215, 215)
COLOR_OF_SLOWZONE = (205, 205, 205)
COLOR_OF_HP = (100, 200, 100)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

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
DARK_BROWN = (109, 72, 51)


def draw_battlefield():
    size = (SIZE_OF_BATTLEFIELD, SIZE_OF_BATTLEFIELD)
    battlefield = pygame.Surface(size)
    battlefield.fill(COLOR_OF_SLOWZONE)
    
    rect = (SIZE_OF_SLOWZONE, SIZE_OF_SLOWZONE, SIZE_OF_BATTLEFIELD-2*SIZE_OF_SLOWZONE, SIZE_OF_BATTLEFIELD-2*SIZE_OF_SLOWZONE)
    pygame.gfxdraw.box(battlefield, rect, COLOR_OF_BATTLEFIELD)

    # 網格
    for x in range(0, SIZE_OF_BATTLEFIELD, 25):
        pygame.gfxdraw.box(battlefield, (x,0,2,SIZE_OF_BATTLEFIELD), COLOR_OF_GRID)
    for y in range(0, SIZE_OF_BATTLEFIELD, 25):
        pygame.gfxdraw.box(battlefield, (0,y,SIZE_OF_BATTLEFIELD,2), COLOR_OF_GRID)

    pygame.image.save(battlefield, "materials/battlefield.png")

def draw_tank_and_bullet():
    for color, body_color, border_color in (("blue",BLUE,DARK_BLUE), ("purple",PURPLE,DARK_PURPLE), ("red",RED,DARK_RED), ("green",GREEN,DARK_GREEN)):
        for scale_of_barrel in (1.00, 0.96, 0.92, 0.88, 0.84):

            tank = pygame.Surface((SIZE_OF_TANK, SIZE_OF_TANK))
            
            border = SIZE_OF_TANK // 35
            
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

            pygame.image.save(tank, f"materials/{color}-tank-{scale_of_barrel}.png")

        # 子彈
        bullet = pygame.Surface((SIZE_OF_BULLET, SIZE_OF_BULLET))
        x = SIZE_OF_BULLET // 2
        y = SIZE_OF_BULLET // 2
        r = x
        pygame.gfxdraw.filled_circle(bullet, x, y, r, border_color)
        border = SIZE_OF_BULLET // 10
        r -= border
        pygame.gfxdraw.filled_circle(bullet, x, y, r, body_color)

        pygame.image.save(bullet, f"materials/{color}-bullet.png")

def draw_mothership():
    num_of_edge = 12
    
    border = SIZE_OF_MOTHERSHIP / 80

    angle = 360 / num_of_edge
    angle_offset = angle / 2

    center = (SIZE_OF_MOTHERSHIP / 2, SIZE_OF_MOTHERSHIP / 2)

    for scale_of_barrel in (1.00, 0.96, 0.92, 0.88, 0.84):
        mothership = pygame.Surface((SIZE_OF_MOTHERSHIP, SIZE_OF_MOTHERSHIP))

        # 母艦砲管
        scale_of_barrel = round(scale_of_barrel, 2)
        w = SIZE_OF_MOTHERSHIP / 2.2 * (scale_of_barrel ** 0.5)
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

        pygame.image.save(mothership, f"materials/mothership-{scale_of_barrel}.png")

def draw_trigonship():
    trigonship = pygame.Surface((SIZE_OF_LITTLESHIP, SIZE_OF_LITTLESHIP))

    x1 = 0
    y1 = 0
    x2 = 0
    y2 = SIZE_OF_LITTLESHIP
    x3 = SIZE_OF_LITTLESHIP
    y3 = SIZE_OF_LITTLESHIP // 2

    pygame.gfxdraw.filled_trigon(trigonship, x1, y1, x2, y2, x3, y3, DARK_BROWN)
    
    border = SIZE_OF_LITTLESHIP // 12

    x1 += border
    y1 += 2 * border
    x2 += border
    y2 -= 2 * border
    x3 -= 5 * border // 2
    y3 = y3

    pygame.gfxdraw.filled_trigon(trigonship, x1, y1, x2, y2, x3, y3, BROWN)

    pygame.image.save(trigonship, "materials/trigonship.png")

def draw_squareship():
    squareship = pygame.Surface((SIZE_OF_LITTLESHIP, SIZE_OF_LITTLESHIP))
    squareship.fill(DARK_BROWN)
    border = 5
    x = border
    y = border
    w = SIZE_OF_LITTLESHIP - 2*border
    h = SIZE_OF_LITTLESHIP - 2*border
    pygame.gfxdraw.box(squareship, (x,y,w,h), BROWN)
    pygame.image.save(squareship, "materials/squareship.png")

def draw_pentagonship():
    pentagonship = pygame.Surface((SIZE_OF_LITTLESHIP, SIZE_OF_LITTLESHIP))
    v = pygame.math.Vector2(SIZE_OF_LITTLESHIP/2, 0)
    center = [SIZE_OF_LITTLESHIP/2, SIZE_OF_LITTLESHIP/2]

    pnts = [v.rotate(angle)+center for angle in range(0, 360, 360//5)]
    pygame.gfxdraw.filled_polygon(pentagonship, pnts, DARK_BROWN)

    border = SIZE_OF_LITTLESHIP / 10
    v -= (border, 0)

    pnts = [v.rotate(angle)+center for angle in range(0, 360, 360//5)]
    pygame.gfxdraw.filled_polygon(pentagonship, pnts, BROWN)

    pygame.image.save(pentagonship, "materials/pentagonship.png")

def draw_cross():
    cross = pygame.Surface((SIZE_OF_CROSS, SIZE_OF_CROSS))

    x = SIZE_OF_CROSS // 4
    y = 0
    w = SIZE_OF_CROSS // 2
    h = SIZE_OF_CROSS
    pygame.gfxdraw.box(cross, (x,y,w,h), DARK_YELLOW)
    x = 0
    y = SIZE_OF_CROSS // 4
    w = SIZE_OF_CROSS
    h = SIZE_OF_CROSS // 2
    pygame.gfxdraw.box(cross, (x,y,w,h), DARK_YELLOW)

    border = SIZE_OF_CROSS // 15

    x = SIZE_OF_CROSS // 4 + border
    y = 0 + border
    w = SIZE_OF_CROSS // 2 - 2 * border
    h = SIZE_OF_CROSS - 2 * border
    pygame.gfxdraw.box(cross, (x,y,w,h), YELLOW)
    x = 0 + border
    y = SIZE_OF_CROSS // 4 + border
    w = SIZE_OF_CROSS - 2 * border
    h = SIZE_OF_CROSS // 2 - 2 * border
    pygame.gfxdraw.box(cross, (x,y,w,h), YELLOW)

    pygame.image.save(cross, "materials/cross.png")

def draw_start_menu_label():
    pygame.font.init()

    font = pygame.font.Font("C:/Windows/Fonts/calibrib.ttf", 150)

    surface = font.render("Die", True, DARK_GRAY)
    pygame.image.save(surface, f"materials/Die.png")
    surface = font.render("py", True, BLUE)
    pygame.image.save(surface, f"materials/py.png")

    font = pygame.font.Font("C:/Windows/Fonts/calibrib.ttf", 70)

    words = ["Play", "New", "Connect"]
    for word in words:
        surface = font.render(word, True, DARK_GRAY)
        pygame.image.save(surface, f"materials/{word}.png")
        surface = font.render(word, True, BLUE)
        pygame.image.save(surface, f"materials/mouseon-{word}.png")

def draw_skill_panel_label():
    pygame.font.init()

    label = pygame.Surface((200, 35))
    
    font = pygame.font.Font("C:/Windows/Fonts/calibrib.ttf", 20)

    for word in ("Barrel", "Reload Time", "Bullet Damage", "Bullet Speed", "Movement Speed"):
        for lv in range(6):
            label.fill(DARK_GRAY)
            pygame.gfxdraw.box(label, (3,3,194,29), GRAY)
            w = 39 * lv
            pygame.gfxdraw.box(label, (3,3,w,29), GREEN)
            surface = font.render(word, True, WHITE)
            x = (200 - surface.get_width()) // 2
            label.blit(surface, (x,9))
            pygame.image.save(label, f"materials/{word}-{lv}.png")

def draw_hpbar():
    hpbar = pygame.Surface((50, 10))
        
    pygame.image.save(hpbar, f"materials/hpbar-0.png")
    pygame.image.save(hpbar, f"materials/hpbar-50.png")

    for rw in range(2, 50, 2):
        hpbar = pygame.Surface((50, 10))

        # 黑
        pygame.gfxdraw.filled_circle(hpbar, 5, 5, 5, DARK_GRAY)
        pygame.gfxdraw.box(hpbar, (5, 0, 40, 10), DARK_GRAY)
        pygame.gfxdraw.filled_circle(hpbar, 45, 5, 5, DARK_GRAY)
        
        # 綠
        pygame.gfxdraw.filled_circle(hpbar, 5, 5, 3, COLOR_OF_HP)
        pygame.gfxdraw.box(hpbar, (5, 2, rw-5, 6), COLOR_OF_HP)
        pygame.gfxdraw.filled_circle(hpbar, rw-5, 5, 3, COLOR_OF_HP)
    
        pygame.image.save(hpbar, f"materials/hpbar-{rw}.png")

# 若素材不存在則產生
if not os.path.isdir("materials"):
    os.mkdir("materials")
    draw_battlefield()
    draw_tank_and_bullet()
    draw_mothership()
    draw_trigonship()
    draw_squareship()
    draw_pentagonship()
    draw_cross()
    draw_start_menu_label()
    draw_skill_panel_label()
    draw_hpbar()

if __name__ != "__main__":
    MATERIALS = {}

    # 載入戰場
    MATERIALS["battlefield"] = pygame.image.load("materials/battlefield.png")

    # 載入背景用於更新畫面
    MATERIALS["background"] = MATERIALS["battlefield"].copy()

    # 載入坦克和子彈
    for color in ("red", "green", "blue", "purple"):
        MATERIALS[f"{color}-tank-1.0"] =  pygame.image.load(f"materials/{color}-tank-1.0.png")
        MATERIALS[f"{color}-tank-0.96"] = pygame.image.load(f"materials/{color}-tank-0.96.png")
        MATERIALS[f"{color}-tank-0.92"] = pygame.image.load(f"materials/{color}-tank-0.92.png")
        MATERIALS[f"{color}-tank-0.88"] = pygame.image.load(f"materials/{color}-tank-0.88.png")
        MATERIALS[f"{color}-tank-0.84"] = pygame.image.load(f"materials/{color}-tank-0.84.png")
        MATERIALS[f"{color}-bullet"] =    pygame.image.load(f"materials/{color}-bullet.png")

    # 載入敵艦
    MATERIALS["mothership-1.0"] =  pygame.image.load(f"materials/mothership-1.0.png")
    MATERIALS["mothership-0.96"] = pygame.image.load(f"materials/mothership-0.96.png")
    MATERIALS["mothership-0.92"] = pygame.image.load(f"materials/mothership-0.92.png")
    MATERIALS["mothership-0.88"] = pygame.image.load(f"materials/mothership-0.88.png")
    MATERIALS["mothership-0.84"] = pygame.image.load(f"materials/mothership-0.84.png")

    MATERIALS["trigonship"] = pygame.image.load(f"materials/trigonship.png")
    MATERIALS["squareship"] = pygame.image.load(f"materials/squareship.png")
    MATERIALS["pentagonship"] = pygame.image.load(f"materials/pentagonship.png")

    # 載入升級十字
    MATERIALS["cross"] = pygame.image.load(f"materials/cross.png")

    # 載入血條
    for i in range(0, 52, 2):
        MATERIALS[f"hpbar-{i}"] = pygame.image.load(f"materials/hpbar-{i}.png")

    # 載入能力值面板
    for word in ("Barrel", "Reload Time", "Bullet Damage", "Bullet Speed", "Movement Speed"):
        for lv in range(6):
            MATERIALS[f"{word}-{lv}"] = pygame.image.load(f"materials/{word}-{lv}.png")
    
    # 將剩餘黑色設為透明
    for image_key in MATERIALS:
        if image_key != "battlefield" and image_key != "background":
            MATERIALS[image_key].set_colorkey(BLACK)
