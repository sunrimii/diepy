from random import randrange, choice
from math import atan2, degrees, ceil
import pickle
import zlib

import pygame
import pygame.freetype

from material import SIZE_OF_BATTLEFIELD, SIZE_OF_SLOWZONE, SIZE_OF_BULLET

# 定義顏色
BLACK = (0, 0, 0)
WHITE = (250, 250, 250)
COLOR_OF_HP = (100, 200, 100)


class Tank(pygame.sprite.Sprite):
    def __init__(self, group, img):
        super().__init__()
        
        # 可升級的能力值
        self.num_of_barrel = 1
        self.reloading_time = 1
        self.damage_of_bullet = 1
        self.speed_of_bullet = 3.5
        self.max_speed = 2.3

        self.hp = 20
        self.damage = 12345
        
        self.pos = (randrange(SIZE_OF_SLOWZONE,SIZE_OF_BATTLEFIELD-SIZE_OF_SLOWZONE), randrange(SIZE_OF_SLOWZONE,SIZE_OF_BATTLEFIELD-SIZE_OF_SLOWZONE))
        self.pos = pygame.math.Vector2(self.pos)
        self.speed = pygame.math.Vector2(0, 0)
        self.acc = 0.03
        self.recoil = pygame.math.Vector2(0.01, 0)
        
        self.bullets = group
        self.is_reloading = False
        self.time_of_attacking = 0
        self.reloading_time = 200
        
        self.IMG = img
        self.image = self.IMG["1.0"]
        self.rect = self.image.get_rect(center=self.pos)
        
        self.cam = pygame.Rect(0, 0, 1920, 1080)
        self.cam.center = self.rect.center
        
    def update(self, event):
        pressed_keys, is_click, pos_of_mouse = event

        # 加上鏡頭位置的偏移
        pos_of_mouse += pygame.math.Vector2(self.cam.topleft)
        # 旋轉角度(https://stackoverflow.com/questions/10473930/how-do-i-find-the-angle-between-2-points-in-pygame)
        # 注意遊戲座標與常用座標不同(Y軸相反)使用時須加上負號
        dx, dy = pos_of_mouse - self.pos
        degs = degrees(atan2(-dy, dx))

        # 左鍵發射子彈
        if (not self.is_reloading) and is_click:
            self.is_reloading = True
            self.time_of_attacking = pygame.time.get_ticks()
            if self.num_of_barrel == 1:
                bullet = Bullet(self.IMG, self.pos, degs, self.damage_of_bullet, self.speed_of_bullet)
                self.bullets.add(bullet)
        
        # 若發射後的冷卻期間伸縮砲管
        if self.is_reloading:
            # 從發射後所經過的時間
            elapsed_time = pygame.time.get_ticks() - self.time_of_attacking
            # 冷卻結束
            if elapsed_time >= self.reloading_time:
                self.is_reloading = False
            # 後25%的時間拉長 有反方向的後座力
            elif elapsed_time > self.reloading_time*0.5:
                self.image = pygame.transform.rotate(self.IMG["1.0"], degs)
                self.speed += self.recoil.rotate(180-degs)
            elif elapsed_time > self.reloading_time*0.45:
                self.image = pygame.transform.rotate(self.IMG["0.96"], degs)
                self.speed += self.recoil.rotate(180-degs)
            elif elapsed_time > self.reloading_time*0.4:
                self.image = pygame.transform.rotate(self.IMG["0.92"], degs)
                self.speed += self.recoil.rotate(180-degs)
            elif elapsed_time > self.reloading_time*0.35:
                self.image = pygame.transform.rotate(self.IMG["0.88"], degs)
                self.speed += self.recoil.rotate(180-degs)
            elif elapsed_time > self.reloading_time*0.3:
                self.image = pygame.transform.rotate(self.IMG["0.84"], degs)
                self.speed += self.recoil.rotate(180-degs)
            # 前25%的時間收縮
            elif elapsed_time > self.reloading_time*0.25:
                self.image = pygame.transform.rotate(self.IMG["0.84"], degs)
            elif elapsed_time > self.reloading_time*0.2:
                self.image = pygame.transform.rotate(self.IMG["0.88"], degs)
            elif elapsed_time > self.reloading_time*0.15:
                self.image = pygame.transform.rotate(self.IMG["0.92"], degs)
            elif elapsed_time > self.reloading_time*0.1:
                self.image = pygame.transform.rotate(self.IMG["0.96"], degs)
            elif elapsed_time > self.reloading_time*0.05:
                self.image = pygame.transform.rotate(self.IMG["1.0"], degs)
        # 縱使沒有發射也要更新
        else:
            self.image = pygame.transform.rotate(self.IMG["1.0"], degs)

        # 將剩餘黑色區域設為透明
        self.image.set_colorkey(BLACK)
        
        # 碰撞檢測用
        self.mask = pygame.mask.from_surface(self.image)

        # 上下加速度
        if pressed_keys[pygame.K_w]:
            self.speed -= (0, self.acc)
        elif pressed_keys[pygame.K_s]:
            self.speed += (0, self.acc)
        elif abs(self.speed.y) > 0.001:
            self.speed.y /= 1.01
        elif abs(self.speed.y) > 0:
            self.speed.y = 0
        # 左右加速度
        if pressed_keys[pygame.K_a]:
            self.speed -= (self.acc, 0)
        elif pressed_keys[pygame.K_d]:
            self.speed += (self.acc, 0)
        elif abs(self.speed.x) > 0.001:
            self.speed.x /= 1.01
        elif abs(self.speed.x) > 0:
            self.speed.x = 0

        # 若進入地圖邊緣會減速
        x_in_slowzone = not(300 < self.pos.x < SIZE_OF_BATTLEFIELD-300)
        y_in_slowzone = not(300 < self.pos.y < SIZE_OF_BATTLEFIELD-300)
        if x_in_slowzone or y_in_slowzone:
            self.speed /= 1.05
        
        # 限制移動速度
        self.speed.x = min(self.max_speed, max(-self.max_speed, self.speed.x))
        self.speed.y = min(self.max_speed, max(-self.max_speed, self.speed.y))
        
        # 限制移動邊界
        self.pos += self.speed
        self.pos.x = min(max(self.pos.x, 0), SIZE_OF_BATTLEFIELD)
        self.pos.y = min(max(self.pos.y, 0), SIZE_OF_BATTLEFIELD)
        self.rect = self.image.get_rect(center=self.pos)

        # 使鏡頭平滑移動
        self.cam.center += (pygame.math.Vector2(self.pos)-self.cam.center) * 0.03

        # 限制移動邊界
        self.cam.x = min(max(self.cam.x, 0), SIZE_OF_BATTLEFIELD-self.cam.w)
        self.cam.y = min(max(self.cam.y, 0), SIZE_OF_BATTLEFIELD-self.cam.h)

        # 碰撞檢測
        # if self.is_alive:
        #     for enemy in pygame.sprite.spritecollide(self, game.enemies, False, pygame.sprite.collide_mask):
        #         if enemy.hp > 0:
        #             pass
        #             # self.is_alive = False
        #     for bullet_pack in pygame.sprite.spritecollide(self, game.bullet_packs, False, pygame.sprite.collide_mask):
        #         if bullet_pack.is_alive:
        #             self.num_of_bullets += bullet_pack.num_of_bullets
        #             bullet_pack.is_alive = False

class Bullet(pygame.sprite.Sprite):
    def __init__(self, IMG, pos, degs, damage, speed):
        super().__init__()
        
        # 可升級的能力
        self.damage = damage
        self.speed = pygame.math.Vector2(speed, 0).rotate(-degs)
        
        self.hp = 1
        
        self.image = IMG["bullet"].copy()
        self.image.set_colorkey(BLACK)
        self.image.set_alpha(0)
        self.mask = IMG["mask_of_bullet"]
        
        # 將起始位置從坦克中心移至砲口
        offset = pygame.math.Vector2(self.speed)
        offset.scale_to_length(50)
        self.pos = pos + offset
        self.rect = self.image.get_rect(center=self.pos)
        
        self.time_of_birth = pygame.time.get_ticks()
        
        # 紀錄碰撞過的敵人 避免短時間內不斷檢測
        self.whitelist = pygame.sprite.Group()
        
    def update(self):
        self.pos += self.speed
        self.rect.center = self.pos
        
        # 外觀動畫
        alive_time = pygame.time.get_ticks() - self.time_of_birth
        if (alive_time < 1500) and (self.hp > 0 ) and (self.image.get_alpha() != 255):
            # 出生時淡入
            alpha = self.image.get_alpha() + 15
            self.image.set_alpha(alpha)
        elif (self.hp <= 0) or (alive_time > 1500):
            # 消失時放大
            scale = [int(SIZE_OF_BULLET*1.03)] * 2
            self.image = pygame.transform.scale(self.image, scale)
            self.rect.size = self.image.get_size()
            # 消失時淡出
            alpha = self.image.get_alpha() - 20
            self.image.set_alpha(alpha)
            # 完全淡出後刪除
            if self.image.get_alpha() is 0:
                del self

        # 碰撞檢測
        # if self.hp > 0:
        #     for enemy in pygame.sprite.spritecollide(self, game.enemies, False, pygame.sprite.collide_mask):
        #         if enemy.hp > 0:
        #             self.is_alive = False
        #             enemy.hp -= 1
        #             #do something

class Game:
    def init_server(self):
        pygame.display.set_mode((1920,1080))
        self.player = {}
        self.clock = pygame.time.Clock()

    def init_client(self):
        pygame.display.set_caption("Diepy")
        icon = pygame.image.load("icon.png")
        pygame.display.set_icon(icon)
        self.screen = pygame.display.set_mode((1920, 1080))
        self.is_running = True

    def add_player(self, addr):
        self.player[addr] = {}
        self.player[addr]["bullets"] = pygame.sprite.Group()
        group = self.player[addr]["bullets"]
        color = choice(self.remaining_color)
        tank = Tank(group, color)
        self.player[addr]["tank"] = pygame.sprite.GroupSingle(tank)
        # 預設輸入事件 使精靈組初始得以更新
        self.player[addr]["event"] = (0,)*323, False, (0,0)
        
    def load_material(self):
        # 載入戰場
        self.BATTLEFIELD = pygame.image.load("material/battlefield.png").convert()
        
        # 背景用於更新畫面
        self.BG = self.BATTLEFIELD.copy()
        
        # 載入坦克和子彈
        self.RED_IMG = {}
        self.RED_IMG["1.0"] =    pygame.image.load(f"material/RED-tank-1.0.png").convert()
        self.RED_IMG["0.96"] =   pygame.image.load(f"material/RED-tank-0.96.png").convert()
        self.RED_IMG["0.92"] =   pygame.image.load(f"material/RED-tank-0.92.png").convert()
        self.RED_IMG["0.88"] =   pygame.image.load(f"material/RED-tank-0.88.png").convert()
        self.RED_IMG["0.84"] =   pygame.image.load(f"material/RED-tank-0.84.png").convert()
        self.RED_IMG["bullet"] = pygame.image.load(f"material/RED-bullet.png").convert()
        self.YELLOW_IMG = {}
        self.YELLOW_IMG["1.0"] =    pygame.image.load(f"material/yellow-tank-1.0.png").convert()
        self.YELLOW_IMG["0.96"] =   pygame.image.load(f"material/yellow-tank-0.96.png").convert()
        self.YELLOW_IMG["0.92"] =   pygame.image.load(f"material/yellow-tank-0.92.png").convert()
        self.YELLOW_IMG["0.88"] =   pygame.image.load(f"material/yellow-tank-0.88.png").convert()
        self.YELLOW_IMG["0.84"] =   pygame.image.load(f"material/yellow-tank-0.84.png").convert()
        self.YELLOW_IMG["bullet"] = pygame.image.load(f"material/yellow-bullet.png").convert()
        self.GREEN_IMG = {}
        self.GREEN_IMG["1.0"] =    pygame.image.load(f"material/green-tank-1.0.png").convert()
        self.GREEN_IMG["0.96"] =   pygame.image.load(f"material/green-tank-0.96.png").convert()
        self.GREEN_IMG["0.92"] =   pygame.image.load(f"material/green-tank-0.92.png").convert()
        self.GREEN_IMG["0.88"] =   pygame.image.load(f"material/green-tank-0.88.png").convert()
        self.GREEN_IMG["0.84"] =   pygame.image.load(f"material/green-tank-0.84.png").convert()
        self.GREEN_IMG["bullet"] = pygame.image.load(f"material/green-bullet.png").convert()
        self.BLUE_IMG = {}
        self.BLUE_IMG["1.0"] =    pygame.image.load(f"material/blue-tank-1.0.png").convert()
        self.BLUE_IMG["0.96"] =   pygame.image.load(f"material/blue-tank-0.96.png").convert()
        self.BLUE_IMG["0.92"] =   pygame.image.load(f"material/blue-tank-0.92.png").convert()
        self.BLUE_IMG["0.88"] =   pygame.image.load(f"material/blue-tank-0.88.png").convert()
        self.BLUE_IMG["0.84"] =   pygame.image.load(f"material/blue-tank-0.84.png").convert()
        self.BLUE_IMG["bullet"] = pygame.image.load(f"material/blue-bullet.png").convert()

        # 碰撞檢測用
        self.RED_IMG["mask_of_bullet"] = pygame.mask.from_surface(self.BLUE_IMG["bullet"])
        self.YELLOW_IMG["mask_of_bullet"] = self.RED_IMG["mask_of_bullet"]
        self.GREEN_IMG["mask_of_bullet"] = self.RED_IMG["mask_of_bullet"]
        self.BLUE_IMG["mask_of_bullet"] = self.RED_IMG["mask_of_bullet"]

        # 分配玩家顏色用
        self.remaining_color = [self.RED_IMG, self.YELLOW_IMG, self.GREEN_IMG, self.BLUE_IMG]

    def get_event(self):
        pressed_keys = pygame.key.get_pressed()
        is_click = pygame.mouse.get_pressed()[0]
        pos_of_mouse = pygame.mouse.get_pos()

        # 關閉遊戲
        if pressed_keys[pygame.K_ESCAPE]:
            self.is_running = False
        
        # 關閉遊戲
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

        event = pickle.dumps((pressed_keys, is_click, pos_of_mouse))

        return event

    def handle_event(self, addr, event):
        event = pickle.loads(event)
        self.player[addr]["event"] = event

    def run_logic(self):
        for each in self.player.values():
            # 更新精靈
            each["tank"].update(each["event"])
            each["bullets"].update()
            # 復原戰場
            each["tank"].clear(self.BATTLEFIELD, self.BG)
            each["bullets"].clear(self.BATTLEFIELD, self.BG)
            # 重畫戰場
            each["tank"].draw(self.BATTLEFIELD) 
            each["bullets"].draw(self.BATTLEFIELD) 

        # 設定刷新率
        self.clock.tick(144)

    def get_screen_data(self, addr):
        # 將戰場切出鏡頭所需的畫面
        surface = self.BATTLEFIELD.subsurface(self.player[addr]["tank"].sprite.cam)
        # 畫面轉位元組
        string = pygame.image.tostring(surface, "RGB")
        # 壓縮
        data = zlib.compress(string)

        return data

    def parse_screen_data(self, data):
        # 解壓縮
        string = zlib.decompress(data)
        # 位元組轉畫面
        surface = pygame.image.frombuffer(string, (1920,1080), "RGB")
        # 更新螢幕
        self.screen.blit(surface, (0,0))
        pygame.display.update()