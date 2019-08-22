import math

from material import *


class Bullet(pygame.sprite.Sprite):
    def __init__(self, color, pos, degs, damage, speed):
        super().__init__()
        
        # 可升級的能力
        self.damage = damage
        self.speed = pygame.math.Vector2(speed, 0).rotate(-degs)

        self.hp = 1

        self.image_key = f"{color}-bullet"
        self.image = MATERIALS[self.image_key].copy()
        self.image_alpha = 0

        # 將起始位置從坦克中心移至砲口
        offset = pygame.math.Vector2(self.speed)
        offset.scale_to_length(50)
        self.pos = pos + offset
        self.rect = self.image.get_rect(center=self.pos)
        
        self.time_of_birth = pygame.time.get_ticks()
        
        self.mask = MATERIALS["bullet-mask"]

        # 紀錄碰撞過的敵人 避免短時間內不斷檢測
        self.whitelist = pygame.sprite.Group()

    def _update_image_fadein_fadeout(self):
        if hasattr(self, "time_of_birth"):
            alive_time = pygame.time.get_ticks() - self.time_of_birth
        else:
            alive_time = 0

        if (alive_time < 1500) and (self.hp > 0) and (self.image_alpha <= 255):
            # 剛發射時淡入
            self.image_alpha += 5
        
        elif (self.hp <= 0) or (alive_time > 1500):
            self.damage = 0

            # 消失時放大
            scale = int(self.image.get_width()*1.004), int(self.image.get_height()*1.004)
            self.image = pygame.transform.scale(self.image, scale)
            self.rect.size = self.image.get_size()
            
            # 消失時淡出
            self.image_alpha -= 10
            
            # 完全淡出後刪除
            if self.image_alpha <= 0:
                self.kill()
    
    def _update_pos(self):
        self.pos += self.speed

        # 限制移動邊界
        self.pos.x = min(max(self.pos.x, 0), SIZE_OF_BATTLEFIELD)
        self.pos.y = min(max(self.pos.y, 0), SIZE_OF_BATTLEFIELD)

        self.rect.center = self.pos
    
    def update(self):
        self._update_pos()
        self._update_image_fadein_fadeout()

        # 碰撞檢測
        # if self.hp > 0:
        #     for enemy in pygame.sprite.spritecollide(self, game.enemies, False, pygame.sprite.collide_mask):
        #         if enemy.hp > 0:
        #             self.is_alive = False
        #             enemy.hp -= 1
        #             #do something
      
class Trigonship(Bullet):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.max_hp = 3
        self.hp = self.max_hp
        self.damage = 1
        
        self.image_alpha = 0

    def _update_target(self, tanks):
        # 追蹤最接近的坦克
        if isinstance(tanks, dict):
            tanks = [group_single.sprite for group_single in tanks.values()]
            self.target = min(tanks, key=self.pos.distance_squared_to)
        else:
            self.target = tanks.sprite

    def _update_speed(self):
        # 旋轉角度(https://stackoverflow.com/questions/10473930/how-do-i-find-the-angle-between-2-points-in-pygame)
        # 注意遊戲座標與常用座標不同(Y軸相反)使用時須加上負號
        dx, dy = self.target.pos - self.pos
        self.image_degs = math.degrees(math.atan2(-dy, dx))
        self.speed.rotate_ip(self.image_degs)

    def _update_image_rotation(self):
        self.image = pygame.transform.rotate(MATERIALS[self.image_key], self.image_degs)
        self.rect.size = self.image.get_size()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, tanks):
        self._update_target(tanks)
        self._update_speed()
        self._update_image_rotation()
        super().update()

class Mothership(Trigonship):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.max_hp = 5000
        self.hp = self.max_hp
        self.damage = 99999

        # 隨機初始位置
        pos = np.random.randint(
            low=SIZE_OF_SLOWZONE,
            high=SIZE_OF_BATTLEFIELD - SIZE_OF_SLOWZONE,
            size=2)
        
        # self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.pos = pygame.math.Vector2(800,800)
        self.speed = pygame.math.Vector2(0.02, 0)
        
        self.ships = pygame.sprite.Group()
        self.is_reloading = False
        self.time_of_attacking = 0
        self.reloading_time = 500

        self.image_series = "mothership"
        self.image_key = f"{self.image_series}-1.0"
        self.image = MATERIALS[self.image_key]
        self.image_degs = 0
        self.image_alpha = 0
        
        self.rect = self.image.get_rect(center=self.pos)

    def _update_speed(self):
        dx, dy = self.target.pos - self.pos
        degs = math.degrees(math.atan2(-dy, dx))
        self.speed.rotate_ip(degs)
    
    def _update_reloading_time_and_image_key(self):
        # 若發射後的冷卻期間伸縮砲管
        if self.is_reloading:
            # 從發射後所經過的時間
            elapsed_time = pygame.time.get_ticks() - self.time_of_attacking
            # 冷卻結束
            if elapsed_time >= self.reloading_time:
                self.is_reloading = False
            
            # 後25%的時間拉長 有反方向的後座力
            elif elapsed_time > self.reloading_time*0.5:
                self.image_key = f"{self.image_series}-1.0"

                if hasattr(self, "recoil"):
                    self.speed += self.recoil.rotate(180-self.image_degs)
            
            elif elapsed_time > self.reloading_time*0.45:
                self.image_key = f"{self.image_series}-0.96"
            
            elif elapsed_time > self.reloading_time*0.4:
                self.image_key = f"{self.image_series}-0.92"
            
            elif elapsed_time > self.reloading_time*0.35:
                self.image_key = f"{self.image_series}-0.88"
            
            elif elapsed_time > self.reloading_time*0.3:
                self.image_key = f"{self.image_series}-0.84"
            
            # 前25%的時間收縮
            elif elapsed_time > self.reloading_time*0.25:
                self.image_key = f"{self.image_series}-0.84"
            
            elif elapsed_time > self.reloading_time*0.2:
                self.image_key = f"{self.image_series}-0.88"
            
            elif elapsed_time > self.reloading_time*0.15:
                self.image_key = f"{self.image_series}-0.92"
            
            elif elapsed_time > self.reloading_time*0.1:
                self.image_key = f"{self.image_series}-0.96"
            
            elif elapsed_time > self.reloading_time*0.05:
                self.image_key = f"{self.image_series}-1.0"
        
        # 縱使沒有發射也要更新
        else:
            self.image_key = f"{self.image_series}-1.0"
   
    def _update_image_rotation(self):
        if self.image_degs < 360:
            self.image_degs += 0.01
        else:
            self.image_degs = 0

        super()._update_image_rotation()

    def update(self, tanks):
        self._update_reloading_time_and_image_key()
        super().update(tanks)

class Tank(Mothership):
    def __init__(self, color):
        pygame.sprite.Sprite.__init__(self)
        
        self.color = color
        
        # 可升級的能力值
        self.num_of_barrel = 1
        self.reloading_time = 300
        self.damage_of_bullet = 1
        self.speed_of_bullet = 1.3
        self.max_speed = 2.3

        self.max_hp = 20
        self.hp = self.max_hp
        self.damage = 10

        # 隨機初始位置
        pos = np.random.randint(
            low=SIZE_OF_SLOWZONE,
            high=SIZE_OF_BATTLEFIELD - SIZE_OF_SLOWZONE,
            size=2)
        
        # self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.pos = pygame.math.Vector2(500,500)

        self.speed = pygame.math.Vector2(0, 0)
        self.acc = 0.01
        self.recoil = pygame.math.Vector2(0.005, 0)
        
        self.bullets = pygame.sprite.Group()
        self.is_reloading = False
        self.time_of_attacking = 0

        self.image_series = f"{self.color}-tank"
        self.image_key = f"{self.image_series}-1.0"
        self.image = MATERIALS[self.image_key]
        self.image_degs = 0
        self.image_alpha = 0
        
        self.rect = self.image.get_rect(center=self.pos)

        # 初始化鏡頭用於製造手持感
        self.cam = pygame.Rect(0, 0, 1920, 1080)
        self.cam.center = self.pos

        # 限制鏡頭邊界
        self.cam.x = min(max(self.cam.x, 0), SIZE_OF_BATTLEFIELD-self.cam.w)
        self.cam.y = min(max(self.cam.y, 0), SIZE_OF_BATTLEFIELD-self.cam.h)

    def _update_speed(self, pressed_keys):
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
            self.speed /= 1.01
        
        # 限制移動速度
        self.speed.x = min(self.max_speed, max(-self.max_speed, self.speed.x))
        self.speed.y = min(self.max_speed, max(-self.max_speed, self.speed.y))

    def _update_image_rotation(self, pos_of_mouse):
        dx, dy = pos_of_mouse - self.pos
        self.image_degs = math.degrees(math.atan2(-dy, dx))
        Trigonship._update_image_rotation(self)
    
    def _update_cam(self):
        # 使鏡頭平滑移動
        self.cam.center += (pygame.math.Vector2(self.pos)-self.cam.center) * 0.03

        # 限制鏡頭邊界
        self.cam.x = min(max(self.cam.x, 0), SIZE_OF_BATTLEFIELD-self.cam.w)
        self.cam.y = min(max(self.cam.y, 0), SIZE_OF_BATTLEFIELD-self.cam.h)
        
    def update(self, event):
        pressed_keys, is_click, pos_of_mouse = event
        pos_of_mouse += pygame.math.Vector2(self.cam.topleft) # 加上鏡頭位置的偏移

        # 左鍵發射子彈
        if (not self.is_reloading) and is_click:
            self.is_reloading = True
            self.time_of_attacking = pygame.time.get_ticks()

            if self.num_of_barrel == 1:
                bullet = Bullet(self.color, self.pos, self.image_degs, self.damage_of_bullet, self.speed_of_bullet)
                self.bullets.add(bullet)

        self._update_reloading_time_and_image_key()
        self._update_speed(pressed_keys)
        self._update_image_rotation(pos_of_mouse)
        Bullet.update(self)
        self._update_cam()

        

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

class Diepy:
    def __init__(self):
        pygame.init()
        self.is_running = True
        
        # 初始化畫面
        pygame.display.set_caption("Diepy")
        icon = pygame.image.load("icon.png")
        pygame.display.set_icon(icon)
        self.display = pygame.display.set_mode((1920, 1080))
        
        # 初始化時鐘用於限制刷新率上限
        self.clock = pygame.time.Clock()
    
    def load_materials(self):
        for image_key in MATERIALS:
            MATERIALS[image_key] = MATERIALS[image_key].convert()

        # 遮罩用於碰撞檢測
        MATERIALS["bullet-mask"] = pygame.mask.from_surface(MATERIALS["red-bullet"])

    def init_single(self):
        # 初始化精靈組用於更新精靈
        self.tank = pygame.sprite.GroupSingle()

    def init_server(self):
        # 初始化玩字典用於存放所有坦克 {地址: 坦克, ...}
        self.tanks = {}
        
        # 尚未使用的顏色
        self.remaining_color = ["red", "yellow", "green", "blue"]

    def select_mode(self):
        mode = "server"

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

    def run_logic(self, events):
        # 單人模式用
        if isinstance(events, tuple):
            self.tank.update(events)
            self.tank.sprite.bullets.update()
        
        # 伺服器用
        else:
            for addr in events:
                event = events[addr]
                tank = self.tanks[addr]
                
                tank.update(event)
                tank.sprite.bullets.update()

    def get_drawinfo(self):
        """取得所有精靈的繪製資訊"""
        
        drawinfo = []
        for addr in self.tanks:
            key = self.tanks[addr].sprite.image_key
            rect = self.tanks[addr].sprite.rect
            topleft = self.tanks[addr].sprite.rect.topleft
            alpha = self.tanks[addr].sprite.image.get_alpha()
            degs = self.tanks[addr].sprite.image_degs

            drawinfo.append((key, rect, topleft, alpha, degs))

            for bullet in self.tanks[addr].sprite.bullets:
                key = bullet.image_key
                rect = bullet.rect
                topleft = bullet.rect.topleft
                alpha = bullet.image.get_alpha()
                degs = 0

                drawinfo.append((key, rect, topleft, alpha, degs))
    
        return drawinfo

    def get_cams(self):
        """伺服器用於取得每個玩家鏡頭位置"""
        
        cams = {}

        for addr in self.tanks:
            cams[addr] = self.tanks[addr].sprite.cam
    
        return cams

    def update_screen(self, drawinfo=None, cam=None):
        # 伺服器用
        if hasattr(self, "tanks"):
            for tank in self.tanks.values():
                tank.draw(MATERIALS["battlefield"])
                tank.sprite.bullets.draw(MATERIALS["battlefield"])
        
            cam = self.cam

        # 客戶端用
        elif drawinfo:
            for key, rect, topleft, alpha, degs in drawinfo:
                image = None
                no_transform = True
                
                if tuple(rect[2:]) == MATERIALS[key].get_size():
                    image = pygame.transform.scale(MATERIALS[key], rect[2:])
                    no_transform = False

                if degs != 0:
                    image = pygame.transform.rotate(MATERIALS[key], degs)
                    no_transform = False
                
                if no_transform:
                    image = MATERIALS[key]

                image.set_alpha(alpha)

                MATERIALS["battlefield"].blit(image, topleft)
        
        # 單人模式用
        else:
            self.tank.draw(MATERIALS["battlefield"])
            self.tank.sprite.bullets.draw(MATERIALS["battlefield"])

            cam = self.tank.sprite.cam

        # 公用
        self.display.blit(MATERIALS["battlefield"], (0,0), cam)
        self.clock.tick(144)
        pygame.display.update()

        # 伺服器用
        if hasattr(self, "tanks"):
            # 為下一張預先清除畫面
            for tank in self.tanks.values():
                tank.sprite.bullets.clear(MATERIALS["battlefield"], MATERIALS["background"])
                tank.clear(MATERIALS["battlefield"], MATERIALS["background"])
        
        # 客戶端用
        elif drawinfo:
            # 為下一張預先清除畫面
            for _, rect, topleft, _, _ in drawinfo:
                MATERIALS["battlefield"].blit(MATERIALS["background"], topleft, rect)
        
        # 單人模式用
        else:
            # 為下一張預先清除畫面
            self.tank.clear(MATERIALS["battlefield"], MATERIALS["background"])
            self.tank.sprite.bullets.clear(MATERIALS["battlefield"], MATERIALS["background"])
