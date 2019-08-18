import math

from material import *


class Tank(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()
        
        self.color = color
        
        # 可升級的能力值
        self.num_of_barrel = 1
        self.reloading_time = 1
        self.damage_of_bullet = 1
        self.speed_of_bullet = 3.5
        self.max_speed = 2.3

        self.hp = 20
        self.damage = 10

        # 隨機初始位置
        pos = np.random.randint(
            low=SIZE_OF_SLOWZONE,
            high=SIZE_OF_BATTLEFIELD - SIZE_OF_SLOWZONE,
            size=2)
        
        # self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.pos = pygame.math.Vector2(*pos)

        self.speed = pygame.math.Vector2(0, 0)
        self.acc = 0.1
        self.recoil = pygame.math.Vector2(0.01, 0)
        
        self.bullets = pygame.sprite.Group()
        self.is_reloading = False
        self.time_of_attacking = 0
        self.reloading_time = 200

        self.image = MATERIALS[f"{self.color}-tank-1.0"]
        self.rect = self.image.get_rect(center=self.pos)

        # 初始化鏡頭用於製造手持感
        self.cam = pygame.Rect(0, 0, 1920, 1080)
        self.cam.center = self.pos

        # 限制鏡頭邊界
        self.cam.x = min(max(self.cam.x, 0), SIZE_OF_BATTLEFIELD-self.cam.w)
        self.cam.y = min(max(self.cam.y, 0), SIZE_OF_BATTLEFIELD-self.cam.h)

    def update(self, event):
        pressed_keys, is_click, pos_of_mouse = event

        # 加上鏡頭位置的偏移
        pos_of_mouse += pygame.math.Vector2(self.cam.topleft)
        # 旋轉角度(https://stackoverflow.com/questions/10473930/how-do-i-find-the-angle-between-2-points-in-pygame)
        # 注意遊戲座標與常用座標不同(Y軸相反)使用時須加上負號
        dx, dy = pos_of_mouse - self.pos
        degs = math.degrees(math.atan2(-dy, dx))

        # 左鍵發射子彈
        if (not self.is_reloading) and is_click:
            self.is_reloading = True
            self.time_of_attacking = pygame.time.get_ticks()
            if self.num_of_barrel == 1:
                bullet = Bullet(self.color, self.pos, degs, self.damage_of_bullet, self.speed_of_bullet)
                self.bullets.add(bullet)

        # 若發射後的冷卻期間伸縮砲管
        if self.is_reloading:
            # 從發射後所經過的時間
            elapsed_time = pygame.time.get_ticks() - self.time_of_attacking
            # 冷卻結束
            if elapsed_time >= self.reloading_time:
                self.is_reloading = False
            # 後25%的時間拉長 有反方向的後座力 可以改
            elif elapsed_time > self.reloading_time*0.5:
                self.image = pygame.transform.rotate(MATERIALS[f"{self.color}-tank-1.0"], degs)
                self.speed += self.recoil.rotate(180-degs)
            elif elapsed_time > self.reloading_time*0.45:
                self.image = pygame.transform.rotate(MATERIALS[f"{self.color}-tank-0.96"], degs)
                self.speed += self.recoil.rotate(180-degs)
            elif elapsed_time > self.reloading_time*0.4:
                self.image = pygame.transform.rotate(MATERIALS[f"{self.color}-tank-0.92"], degs)
                self.speed += self.recoil.rotate(180-degs)
            elif elapsed_time > self.reloading_time*0.35:
                self.image = pygame.transform.rotate(MATERIALS[f"{self.color}-tank-0.88"], degs)
                self.speed += self.recoil.rotate(180-degs)
            elif elapsed_time > self.reloading_time*0.3:
                self.image = pygame.transform.rotate(MATERIALS[f"{self.color}-tank-0.84"], degs)
                self.speed += self.recoil.rotate(180-degs)
            # 前25%的時間收縮
            elif elapsed_time > self.reloading_time*0.25:
                self.image = pygame.transform.rotate(MATERIALS[f"{self.color}-tank-0.84"], degs)
            elif elapsed_time > self.reloading_time*0.2:
                self.image = pygame.transform.rotate(MATERIALS[f"{self.color}-tank-0.88"], degs)
            elif elapsed_time > self.reloading_time*0.15:
                self.image = pygame.transform.rotate(MATERIALS[f"{self.color}-tank-0.92"], degs)
            elif elapsed_time > self.reloading_time*0.1:
                self.image = pygame.transform.rotate(MATERIALS[f"{self.color}-tank-0.96"], degs)
            elif elapsed_time > self.reloading_time*0.05:
                self.image = pygame.transform.rotate(MATERIALS[f"{self.color}-tank-1.0"], degs)
        # 縱使沒有發射也要更新
        else:
            self.image = pygame.transform.rotate(MATERIALS[f"{self.color}-tank-1.0"], degs)

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

        # 限制鏡頭邊界
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
    def __init__(self, color, pos, degs, damage, speed):
        super().__init__()
        
        # 可升級的能力
        self.damage = damage
        self.speed = pygame.math.Vector2(speed, 0).rotate(-degs)
        
        self.hp = 1
        
        self.image = MATERIALS[f"{color}-bullet"].copy()
        self.mask = MATERIALS["bullet-mask"]
        
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

class Diepy:
    def __init__(self):
        pygame.init()
        self.is_running = True
        
        # 初始化螢幕
        pygame.display.set_caption("Diepy")
        icon = pygame.image.load("icon.png")
        pygame.display.set_icon(icon)
        self.screen = pygame.display.set_mode((1920, 1080))
        
        # 初始化時鐘用於限制刷新率
        self.clock = pygame.time.Clock()
    
    def load_materials(self):
        for image_name in MATERIALS:
            MATERIALS[image_name] = MATERIALS[image_name].convert()
            
        MATERIALS["red-bullet"].set_colorkey(BLACK)
        MATERIALS["yellow-bullet"].set_colorkey(BLACK)
        MATERIALS["green-bullet"].set_colorkey(BLACK)
        MATERIALS["blue-bullet"].set_colorkey(BLACK)

        MATERIALS["red-bullet"].set_alpha(0)
        MATERIALS["yellow-bullet"].set_alpha(0)
        MATERIALS["green-bullet"].set_alpha(0)
        MATERIALS["blue-bullet"].set_alpha(0)
 
        # 遮罩用於碰撞檢測
        MATERIALS["bullet-mask"] = pygame.mask.from_surface(MATERIALS["red-bullet"])
    
    def init_single(self):
        # 初始化精靈組用於更新精靈
        self.tank = pygame.sprite.GroupSingle()

    def init_server(self, addr):
        # 初始化玩字典用於存放所有坦克 {地址: 坦克, ...}
        self.tanks = {}
        
        # 尚未使用的顏色
        self.remaining_color = ["red", "yellow", "green", "blue"]
    
    def init_client(self, addr):
        self.addr = addr
 
    def select_mode(self):
        mode = "single"

        return mode

    def add_player(self, addr=None, serverself=False):
        # 伺服器用
        if addr:
            # 初始化精靈組
            self.tanks[addr] = pygame.sprite.GroupSingle()
            
            # 分配顏色
            color = np.random.choice(self.remaining_color)
            self.remaining_color.remove(color)
        
            # 初始化坦克
            tank = Tank(color)
            self.tanks[addr].add(tank)

            if serverself:
                self.cam = tank.cam
        
        # 單人模式用
        else:
            # 初始化坦克
            tank = Tank("blue")
            self.tank.add(tank)

    def update_screen(self, drawinfo=None, cams=None):
        # 伺服器用 可以改 鎖定部分區域能化的方是
        if hasattr(self, "tanks"):
            for tank in self.tanks.values():
                # 先清除
                tank.clear(MATERIALS["battlefield"], MATERIALS["background"])
                tank.sprite.bullets.clear(MATERIALS["battlefield"], MATERIALS["background"])

                # 再畫
                tank.draw(MATERIALS["battlefield"])
                tank.sprite.bullets.draw(MATERIALS["battlefield"], MATERIALS["background"])
        
            cam = self.cam
        
        # 客戶端用
        elif drawinfo:
            for image_name, rect, alpha in drawinfo:
                image = MATERIALS[image_name]
                image.set_alpha(alpha)
                MATERIALS["battlefield"].blit(image, rect)
        
            cam = cams[self.addr]
        
        # 單人模式用
        else:
            # 先清除
            self.tank.clear(MATERIALS["battlefield"], MATERIALS["background"])
            self.tank.sprite.bullets.clear(MATERIALS["battlefield"], MATERIALS["background"])

            # 再畫
            self.tank.draw(MATERIALS["battlefield"])
            self.tank.sprite.bullets.draw(MATERIALS["battlefield"])

            cam = self.tank.sprite.cam

        # 公用
        sub_battlefield = MATERIALS["battlefield"].subsurface(cam)
        self.screen.blit(sub_battlefield, (0,0))
        self.clock.tick(144)
        pygame.display.update()

        # 客戶端用
        if drawinfo:
            # 為下一張預先清除畫面
            for _, rect, _ in drawinfo:
                sub_background = MATERIALS["background"].subsurface(rect)
                topleft = rect[:2]
                MATERIALS["battlefield"].blit(sub_background, topleft)

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

        event = pressed_keys, is_click, pos_of_mouse

        return event

    def run_logic(self, event):
        # 單人模式用
        if isinstance(event, tuple):
            self.tank.update(event)
            self.tank.sprite.bullets.update()
        
        # 伺服器用
        else:
            for addr in event:
                event = event[addr]
                tank = self.tanks[addr]
                
                tank.update(event)
                tank.sprite.bullets.update()
