import math
import random

from material import *


class Bullet(pygame.sprite.Sprite):
    def __init__(self, color, pos, degs, damage, speed):
        super().__init__()
        
        # 可升級的能力
        self.damage = damage
        self.speed = speed.rotate(-degs)

        self.hp = 1

        # 將起始位置從坦克中心移至砲口
        offset = pygame.math.Vector2(SIZE_OF_TANK/2, 0)
        offset.rotate_ip(-degs)
        self.pos = pos + offset

        self.acc = 0

        self.time_of_birth = pygame.time.get_ticks()
        self.image_key = f"{color}-bullet"
        self.image = MATERIALS[self.image_key].copy()
        self.image_alpha = 0
        self.image_scale = 1

        self.rect = self.image.get_rect(center=self.pos)
        
        self.mask = MATERIALS["bullet-mask"]

    def _update_fadein_fadeout(self, speedup_when_fadein=False):
        alive_time = pygame.time.get_ticks() - self.time_of_birth

        if (alive_time < 500) and (self.hp > 0) and (self.image_alpha < 255):
            # 剛產生時淡入
            self.image.set_alpha(self.image_alpha)
            self.image_alpha += 12

            if speedup_when_fadein:
                self.speed *= 1.1
        
        elif (self.hp <= 0) or (alive_time > 1500 and type(self) == Bullet):
            self.damage = 0

            self.image_scale *= 1.028
            w = int(MATERIALS[self.image_key].get_width() * self.image_scale)
            h = int(MATERIALS[self.image_key].get_height() * self.image_scale)
            self.image = pygame.transform.scale(self.image, (w,h))
            
            self.rect = self.image.get_rect(center=self.pos)
            
            # 消失時淡出
            self.image_alpha -= 12
            self.image.set_alpha(self.image_alpha)

            # 完全淡出後刪除
            if self.image_alpha <= 0:
                self.kill()
                # 系統回收時間過長 因此直接刪除
                del self    
    
    def _update_pos(self):
        self.pos += self.speed
        self.rect.center = self.pos
    
    def _update_collision(self, motherships):
        if self.hp > 0:
            # 偵測母艦碰撞
            collied_motherships = pygame.sprite.spritecollide(self, motherships, False, pygame.sprite.collide_mask)
            for collied_mothership in collied_motherships:
                if collied_mothership.hp > 0:
                    # 互相傷害
                    collied_mothership.hp -= self.damage
                    self.hp = 0
                    return
       
            # 偵測小飛機碰撞
            for mothership in motherships:
                collied_littleships = pygame.sprite.spritecollide(self, mothership.littleships, False, pygame.sprite.collide_mask)
                for collied_littleship in collied_littleships:
                    if collied_littleship.hp > 0:
                        # 互相傷害
                        collied_littleship.hp -= self.damage
                        self.hp = 0
                        return

    def update(self, motherships):
        # 若淡出時每次都放大同張會失真 因此每次更新都換新圖
        self.image = MATERIALS[self.image_key].copy()

        self._update_pos()
        self._update_collision(motherships)
        self._update_fadein_fadeout()
        
class Trigonship(Bullet):
    def __init__(self, pos, degs):
        pygame.sprite.Sprite.__init__(self)

        self.max_hp = 1
        self.hp = self.max_hp
        self.damage = 1

        self.searching_time = 20000
        # 設為負數使一開始就搜尋
        self.time_of_starting_to_search = -self.searching_time

        # 將起始位置從坦克中心移至砲口
        offset = pygame.math.Vector2(SIZE_OF_MOTHERSHIP/2, 0)
        offset.rotate_ip(-degs)
        self.pos = pos + offset

        self.speed = pygame.math.Vector2(1.3, 0)

        self.time_of_birth = pygame.time.get_ticks()
        self.image_key = "trigonship"
        self.image = MATERIALS[self.image_key]
        self.image_alpha = 0
        self.image_scale = 1

        self.rect = self.image.get_rect(center=self.pos)

    def _update_target(self, tanks):
        elapsed_time = pygame.time.get_ticks() - self.time_of_starting_to_search
        
        # 減少搜尋次數提升效能
        if elapsed_time > self.searching_time:
            self.time_of_starting_to_search = pygame.time.get_ticks()

            # 追蹤最接近的坦克
            self.target = min(tanks, key=lambda tank: self.pos.distance_squared_to(tank.pos))
            # self.target = tanks.sprites()[0]
            
    def _update_speed(self):
        # 旋轉角度(https://stackoverflow.com/questions/10473930/how-do-i-find-the-angle-between-2-points-in-pygame)
        # 注意遊戲座標與常用座標不同(Y軸相反)使用時須加上負號
        dx, dy = self.target.pos - self.pos
        self.image_degs = math.degrees(math.atan2(-dy, dx))
        
        self.speed.update(1, 0)
        self.speed.rotate_ip(-self.image_degs)

    def _update_image_rotation(self):
        self.image = pygame.transform.rotate(MATERIALS[self.image_key], self.image_degs)
        self.rect.size = self.image.get_size()
        self.mask = pygame.mask.from_surface(self.image)
    
    def _update_pos(self):
        self.pos += self.speed

        # 限制移動邊界
        self.pos.x = min(max(self.pos.x, 0), SIZE_OF_BATTLEFIELD)
        self.pos.y = min(max(self.pos.y, 0), SIZE_OF_BATTLEFIELD)
        
        self.rect.center = self.pos
    
    def _update_hp(self):
        # 顯示血量條
        if 0 < self.hp < self.max_hp:
            w1, h1 = MATERIALS[self.image_key].get_size()
            w2, h2 = self.image.get_size()
            
            # 黑
            cr = 5
            cx = w2 // 2 - w1 // 10 * 2
            cy = h2 // 2 + h1 // 10 * 4
            pygame.gfxdraw.filled_circle(self.image, cx, cy, cr, DARK_GRAY)
            rx = cx + cr // 2
            ry = cy - cr + 1
            rw = h1 // 10 * 4
            rh = 10
            pygame.gfxdraw.box(self.image, (rx, ry, rw, rh), DARK_GRAY)
            cx += w1 // 10 * 4
            pygame.gfxdraw.filled_circle(self.image, cx, cy, cr, DARK_GRAY)
            
            # 綠
            cr -= 2
            cx = w2 // 2 - w1 // 10 * 2
            pygame.gfxdraw.filled_circle(self.image, cx, cy, cr, COLOR_OF_HP)
            ry += 2
            rh -= 4
            rw = rw * self.hp // self.max_hp
            pygame.gfxdraw.box(self.image, (rx, ry, rw, rh), COLOR_OF_HP)
            cx += rw
            pygame.gfxdraw.filled_circle(self.image, cx, cy, cr, COLOR_OF_HP)
    
    def update(self, tanks):
        self._update_target(tanks)
        self._update_speed()
        self._update_image_rotation()
        self._update_pos()
        self._update_hp()
        self._update_fadein_fadeout(speedup_when_fadein=True)

class Mothership(Trigonship):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.max_hp = 5000
        self.hp = self.max_hp
        self.damage = 0

        # 在緩速區隨機初始位置
        # while True:
        #     pos = random.randint(
        #         low=SIZE_OF_SLOWZONE,
        #         high=SIZE_OF_BATTLEFIELD - SIZE_OF_SLOWZONE,
        #         size=2)
            
        #     x_in_range = SIZE_OF_SLOWZONE <= pos[0] <= SIZE_OF_BATTLEFIELD - SIZE_OF_SLOWZONE
        #     y_in_range = SIZE_OF_SLOWZONE <= pos[1] <= SIZE_OF_BATTLEFIELD - SIZE_OF_SLOWZONE
            
        #     if not (x_in_range and y_in_range):
        #         self.pos = pygame.math.Vector2(pos[0], pos[1])
        #         break
        
        self.pos = pygame.math.Vector2(0, 0)
        self.speed = pygame.math.Vector2(1, 0)
        
        self.searching_time = 20000
        # 設為負數使一開始就搜尋
        self.time_of_starting_to_search = -self.searching_time

        self.littleships = pygame.sprite.Group()
        self.is_reloading = False # 主要用於計算砲管伸縮長度
        self.time_of_starting_to_reload = 0
        self.reloading_time = 300
        self.is_cooling = False # 主要用於計算攻擊時機
        self.time_of_starting_to_cool = 0
        self.cooling_time = 5000

        self.time_of_birth = pygame.time.get_ticks()
        self.image_series = "mothership"
        self.image_key = f"{self.image_series}-1.0"
        self.image = MATERIALS[self.image_key]
        self.image_alpha = 0
        self.image_degs = 0
        self.image_scale = 1
        
        self.rect = self.image.get_rect(center=self.pos)

    def _update_speed(self):
        dx, dy = self.target.pos - self.pos
        degs = math.degrees(math.atan2(dy, dx))
        self.speed.update(0.5, 0)
        self.speed.rotate_ip(degs)
    
    def _update_cooling_time(self):
        if self.is_cooling:
            elapsed_time = pygame.time.get_ticks() - self.time_of_starting_to_cool
            if elapsed_time > self.cooling_time:
                self.is_cooling = False
    
    def _update_reloading_time_and_image_key(self):
        # 若發射後的冷卻期間伸縮砲管
        if self.is_reloading:
            # 從發射後所經過的時間
            elapsed_time = pygame.time.get_ticks() - self.time_of_starting_to_reload
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
            self.image_degs += 0.05
        else:
            self.image_degs = 0

        super()._update_image_rotation()
 
    def update(self, tanks):
        # 自動發射小飛機
        if (not self.is_reloading) and (not self.is_cooling):
            self.is_reloading = True
            self.is_cooling = True
            self.time_of_starting_to_reload = pygame.time.get_ticks()
            self.time_of_starting_to_cool = pygame.time.get_ticks()
            
            for degs in range(0, 360, 360//12):
                trigonship = Trigonship(self.pos, self.image_degs+degs)
                self.littleships.add(trigonship)

        self._update_cooling_time()
        self._update_reloading_time_and_image_key()
        self._update_target(tanks)
        self._update_speed()
        self._update_image_rotation()
        self._update_pos()
        self._update_hp()
        self._update_fadein_fadeout()
        self.littleships.update(tanks)

class Cross(Mothership):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.hp = 1

        # 在非緩速區隨機初始位置
        pos = [random.randint(SIZE_OF_SLOWZONE, SIZE_OF_BATTLEFIELD-SIZE_OF_SLOWZONE) for _ in range(2)]
        self.pos = pygame.math.Vector2(pos)
        self.speed = pygame.math.Vector2(0, 0)

        self.time_of_birth = pygame.time.get_ticks()
        self.image_key = "cross"
        self.image = MATERIALS["cross"]
        self.image_alpha = 0
        self.image_degs = random.randint(0, 359)
        self.image_scale = 1
        
        self.rect = self.image.get_rect(center=self.pos)

    def _update_collision(self, tanks):
        if self.hp > 0:
            # 偵測坦克碰撞
            collied_tanks = pygame.sprite.spritecollide(self, tanks, False, pygame.sprite.collide_mask)
            for collied_tank in collied_tanks:
                if collied_tank.hp > 0:
                    self.hp = 0
                    return

    def update(self, tanks):
        self._update_image_rotation()
        self._update_pos()
        self._update_collision(tanks)
        self._update_fadein_fadeout()
        
class Tank(Mothership):
    def __init__(self, color, addr=None):
        pygame.sprite.Sprite.__init__(self)
        
        if addr:
            self.addr = addr
        
        self.color = color

        self.skill_pnt = 0

        # 可升級的能力值
        self.num_of_barrel = 1
        self.reloading_time = 300
        self.damage_of_bullet = 1
        self.speed_of_bullet = pygame.math.Vector2(1.5, 0)
        self.max_speed = 2.3

        self.max_hp = 2000000
        self.hp = self.max_hp
        self.damage = 10

        # 在非緩速區隨機初始位置
        # pos = [random.randint(SIZE_OF_SLOWZONE, SIZE_OF_BATTLEFIELD-SIZE_OF_SLOWZONE) for _ in range(2)]
        
        # self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.pos = pygame.math.Vector2(500,500)

        self.speed = pygame.math.Vector2(0, 0)
        self.acc = 0.01
        self.recoil = pygame.math.Vector2(0.005, 0)
        
        self.bullets = pygame.sprite.Group()
        self.is_reloading = False
        self.time_of_starting_to_reload = 0

        self.time_of_birth = pygame.time.get_ticks()
        self.image_series = f"{self.color}-tank"
        self.image_key = f"{self.image_series}-1.0"
        self.image = MATERIALS[self.image_key]
        self.image_degs = 0
        self.image_alpha = 0
        self.image_scale = 1
        
        self.rect = self.image.get_rect(center=self.pos)

        # 初始化鏡頭用於製造手持感
        self.cam = pygame.Rect(0, 0, 1920, 1080)
        self.cam_pos = [random.randint(SIZE_OF_SLOWZONE, SIZE_OF_BATTLEFIELD-SIZE_OF_SLOWZONE) for _ in range(2)]
        self.cam.center = self.cam_pos

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

    def _update_image_rotation(self, mouse_pos):
        dx, dy = mouse_pos - self.pos
        self.image_degs = math.degrees(math.atan2(-dy, dx))
        Trigonship._update_image_rotation(self)

    def _update_collision(self, motherships):
        if self.hp > 0:
            # 偵測母艦碰撞
            collied_motherships = pygame.sprite.spritecollide(self, motherships, False, pygame.sprite.collide_mask)
            for collied_mothership in collied_motherships:
                if collied_mothership.hp > 0:
                    # 互相傷害
                    collied_mothership.hp -= self.damage
                    self.hp -= collied_mothership.damage
       
            # 偵測小飛機碰撞
            for mothership in motherships:
                collied_littleships = pygame.sprite.spritecollide(self, mothership.littleships, False, pygame.sprite.collide_mask)
                for collied_littleship in collied_littleships:
                    if collied_littleship.hp > 0:
                        # 互相傷害
                        collied_littleship.hp -= self.damage
                        self.hp -= collied_littleship.damage

    def _update_cam(self):
        # 使鏡頭平滑移動
        self.cam_pos += (self.pos-self.cam_pos) * 0.03
        self.cam.center = self.cam_pos

        # 限制鏡頭邊界
        self.cam.x = min(max(self.cam.x, 0), SIZE_OF_BATTLEFIELD-self.cam.w)
        self.cam.y = min(max(self.cam.y, 0), SIZE_OF_BATTLEFIELD-self.cam.h)
        
    def update(self, events, motherships):
        if type(events) == dict:
            event = events[self.addr]
        else:
            event = events

        pressed_keys, is_clicked, mouse_pos = event
        mouse_pos += pygame.math.Vector2(self.cam.topleft) # 加上鏡頭位置的偏移

        # 左鍵發射子彈
        if (not self.is_reloading) and is_clicked:
            self.is_reloading = True
            self.time_of_starting_to_reload = pygame.time.get_ticks()
            if self.num_of_barrel == 1:
                bullet = Bullet(self.color, self.pos, self.image_degs, self.damage_of_bullet, self.speed_of_bullet)
                self.bullets.add(bullet)

        self._update_reloading_time_and_image_key()
        self._update_speed(pressed_keys)
        self._update_image_rotation(mouse_pos)
        self._update_pos()
        self._update_hp()
        self._update_collision(motherships)
        self._update_fadein_fadeout()
        self._update_cam()
        self.bullets.update(motherships)

class SkillPanel(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image


class Label(pygame.sprite.Sprite):
    def __init__(self, text, topleft, clickable=False, hotkey=None):
        super().__init__()

        self.image = pygame.image.load(f"materials/{text}.png")
        
        self.clickable = clickable
        
        if clickable:
            self.mouseon_image = pygame.image.load(f"materials/mouseon-{text}.png")
            self.mouseoff_image = self.image.copy()

        self.rect = self.image.get_rect(topleft=topleft)

    def update(self, event):
        if self.clickable:
            _, is_clicked, mouse_pos = event

            if self.rect.collidepoint(mouse_pos):
                self.image = self.mouseon_image
                if is_clicked:
                    self.kill()
            else:
                self.image = self.mouseoff_image
     
class Diepy:
    def __init__(self):
        self.is_running = True
        
        # 初始化畫面
        self.display = pygame.display.set_mode((1920, 1080))
        icon = pygame.image.load("icon.png")
        pygame.display.set_icon(icon)
        pygame.display.set_caption("Diepy")
        
        # 初始化時鐘用於限制刷新率上限
        self.clock = pygame.time.Clock()

        self.tanks = pygame.sprite.Group()
        self.motherships = pygame.sprite.Group()
        self.crosses = pygame.sprite.Group()

    def init_server(self):
        # 尚未使用的顏色
        self.remaining_color = ["red", "green", "blue", "purple"]

    def load_materials(self):
        pygame.display.init()
        
        for image_key in MATERIALS:
            MATERIALS[image_key] = MATERIALS[image_key].convert()

        # 遮罩用於碰撞檢測
        MATERIALS["bullet-mask"] = pygame.mask.from_surface(MATERIALS["red-bullet"])

    def select_mode(self):
        # 載入選單用字
        single_label = Label("Play", (800,500), True)
        server_label = Label("New", (800,600), True)
        client_label = Label("Connect", (800,700), True)
        menu = pygame.sprite.RenderUpdates()
        menu.add(Label("Die", (800,200)))
        menu.add(Label("py", (1010,200)))
        menu.add(single_label)
        menu.add(server_label)
        menu.add(client_label)

        self.display.fill((240, 240, 240))
        pygame.display.update()

        self.mode = None
        while not self.mode:
            event = self.get_event()
            menu.update(event)

            changes = menu.draw(self.display)
            self.clock.tick(144)
            pygame.display.update(changes)

            if not menu.has(single_label):
                self.mode = "single"
            elif not menu.has(server_label):
                self.mode = "server"
            elif not menu.has(client_label):
                self.mode = "client"

    def add_tank(self, addr=None, serverself=False):
        if self.mode == "server":
            # 分配顏色
            color = random.choice(self.remaining_color)
            self.remaining_color.remove(color)

            tank = Tank(color, addr)
            self.tanks.add(tank)

            # 伺服器自己的鏡頭資訊紀錄在本地不需傳送
            if serverself:
                self.cam = tank.cam
        
        # 單人模式用
        else:
            # 初始化坦克
            tank = Tank("blue")
            self.tanks.add(tank)

    def add_mothership(self):
        """加入母艦 數量與玩家人數相同"""

        for _ in range(len(self.tanks)):
            self.motherships.add(Mothership())

    def add_cross(self):
        """加入升級十字 產生機率根據玩家人數遞增"""

        if len(self.crosses) < 5:
            max_ = 1000 // len(self.tanks)

            # 只有隨機產生是0時才為真
            if not random.randint(0, max_):
                self.crosses.add(Cross())

    def get_event(self):
        """取得該玩家的輸入事件"""

        pressed_keys = pygame.key.get_pressed()
        is_clicked = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()

        # 關閉遊戲
        if pressed_keys[pygame.K_ESCAPE]:
            self.is_running = False
        
        # 關閉遊戲
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

        event = pressed_keys, is_clicked, mouse_pos

        return event

    def run_logic(self, events):
        """執行主程式邏輯 更新所有精靈"""

        self.tanks.update(events, self.motherships)
        self.motherships.update(self.tanks)
        self.crosses.update(self.tanks)

    def get_drawinfo(self):
        """伺服器用於取得所有精靈的繪製資訊"""
        
        drawinfo = []

        for tank in self.tanks:
            key = tank.image_key
            rect = tank.rect
            topleft = tank.rect.topleft
            alpha = tank.image_alpha
            degs = tank.image_degs

            drawinfo.append((key, rect, topleft, alpha, degs))

            for bullet in tank.bullets:
                key = bullet.image_key
                rect = bullet.rect
                topleft = bullet.rect.topleft
                alpha = bullet.image_alpha
                degs = 0

                drawinfo.append((key, rect, topleft, alpha, degs))
        
        for mothership in self.motherships:
            key = mothership.image_key
            rect = mothership.rect
            topleft = mothership.rect.topleft
            alpha = mothership.image_alpha
            degs = mothership.image_degs

            drawinfo.append((key, rect, topleft, alpha, degs))

            for littleship in mothership.littleships:
                key = littleship.image_key
                rect = littleship.rect
                topleft = littleship.rect.topleft
                alpha = littleship.image_alpha
                degs = littleship.image_degs

                drawinfo.append((key, rect, topleft, alpha, degs))
    
        return drawinfo

    def get_cams(self):
        """伺服器用於取得每個玩家鏡頭位置"""

        cams = {}
        for tank in self.tanks:
            cams[tank.addr] = tank.cam
        return cams

    def update_screen(self, drawinfo=None, cam=None):
        # 畫所有精靈畫在戰場上
        if self.mode == "client":
            for key, rect, topleft, alpha, degs in drawinfo:
                image = None
                no_transform = True
                
                # 若有縮放
                if tuple(rect[2:]) == MATERIALS[key].get_size():
                    image = pygame.transform.scale(MATERIALS[key], rect[2:])
                    no_transform = False

                # 若有旋轉
                if degs != 0:
                    image = pygame.transform.rotate(MATERIALS[key], degs)
                    no_transform = False
                
                if no_transform:
                    image = MATERIALS[key]

                image.set_alpha(alpha)

                MATERIALS["battlefield"].blit(image, topleft)

        else:
            # 畫坦克
            self.tanks.draw(MATERIALS["battlefield"])

            # 畫子彈
            for tank in self.tanks:
                tank.bullets.draw(MATERIALS["battlefield"])
        
            # 畫母艦
            self.motherships.draw(MATERIALS["battlefield"])

            # 畫小飛機
            for mothership in self.motherships:
                mothership.littleships.draw(MATERIALS["battlefield"])

            # 畫升級十字
            self.crosses.draw(MATERIALS["battlefield"])

            # 更新鏡頭位置
            if self.mode == "server":
                cam = self.cam
            # 單人模式用
            else:
                cam = self.tanks.sprites()[0].cam
        
        # 將戰場更新到畫面上
        self.display.blit(MATERIALS["battlefield"], (0,0), cam)
        self.clock.tick(144)
        pygame.display.update()

        # 為下一張預先清除戰場
        if self.mode == "client":
            for _, rect, topleft, _, _ in drawinfo:
                MATERIALS["battlefield"].blit(MATERIALS["background"], topleft, rect)

        else:
            # 清坦克
            self.tanks.clear(MATERIALS["battlefield"], MATERIALS["background"])
            
            # 清子彈
            for tank in self.tanks:
                tank.bullets.clear(MATERIALS["battlefield"], MATERIALS["background"])
            
            # 清母艦
            self.motherships.clear(MATERIALS["battlefield"], MATERIALS["background"])
            
            # 清小飛機
            for mothership in self.motherships:
                mothership.littleships.clear(MATERIALS["battlefield"], MATERIALS["background"])

            # 清升級十字
            self.crosses.clear(MATERIALS["battlefield"], MATERIALS["background"])