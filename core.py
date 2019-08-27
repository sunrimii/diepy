import math
import random

from material import *


class Bullet(pygame.sprite.Sprite):
    def __init__(self, color, pos, degs, damage, speed):
        super().__init__()
        
        self.damage = damage
        self.speed = pygame.math.Vector2(speed, 0)
        self.speed.rotate_ip(-degs)

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

    def _update_fadein_fadeout(self, speedup_when_fadein=None, max_alive_time=None):
        alive_time = pygame.time.get_ticks() - self.time_of_birth

        # 若有設定生命期限
        if max_alive_time and alive_time > max_alive_time:
            self.hp = 0

        if (alive_time < 1000) and (self.hp > 0) and (self.image_alpha < 255):
            # 剛產生時淡入
            self.image.set_alpha(self.image_alpha)
            self.image_alpha += 25

            # 若有設定淡入時加速
            if speedup_when_fadein:
                self.speed *= speedup_when_fadein
        
        elif self.hp <= 0:
            self.damage = 0

            self.image_scale *= 1.028
            w = int(MATERIALS[self.image_key].get_width() * self.image_scale)
            h = int(MATERIALS[self.image_key].get_height() * self.image_scale)
            self.image = pygame.transform.scale(self.image, (w,h))
            
            self.rect = self.image.get_rect(center=self.pos)
            
            # 死亡時淡出
            self.image_alpha -= 20
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
        self._update_fadein_fadeout(max_alive_time=1500)

class Trigonship(Bullet):
    def __init__(self, pos, degs):
        pygame.sprite.Sprite.__init__(self)

        self.max_hp = 2
        self.hp = self.max_hp
        self.damage = 1

        self.search_time = 30000
        # 設為負數使一開始就搜尋
        self.time_of_starting_to_search = -self.search_time

        # 將起始位置從坦克中心移至砲口
        offset = pygame.math.Vector2(SIZE_OF_MOTHERSHIP/2, 0)
        offset.rotate_ip(-degs)
        self.pos = pos + offset

        self.speed = pygame.math.Vector2(0, 0)

        self.time_of_birth = pygame.time.get_ticks()
        self.image_key = "trigonship"
        self.image = MATERIALS[self.image_key]
        self.image_alpha = 0
        self.image_scale = 1

        self.rect = self.image.get_rect(center=self.pos)

        self.hpbar = pygame.sprite.GroupSingle(Hpbar(self.image_key))

    def _update_target(self, tanks):
        elapsed_time = pygame.time.get_ticks() - self.time_of_starting_to_search
        
        # 減少搜尋次數提升效能
        if elapsed_time > self.search_time:
            self.time_of_starting_to_search = pygame.time.get_ticks()

            # 追蹤最接近的坦克
            self.target = min(tanks, key=lambda tank: self.pos.distance_squared_to(tank.pos))
            # self.target = tanks.sprites()[0]
            
    def _update_speed(self):
        # 旋轉角度(https://stackoverflow.com/questions/10473930/how-do-i-find-the-angle-between-2-points-in-pygame)
        # 注意遊戲座標與常用座標不同(Y軸相反)使用時須加上負號
        dx, dy = self.target.pos - self.pos
        self.image_degs = math.degrees(math.atan2(-dy, dx))
        
        self.speed.update(3, 0)
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
    
    def update(self, tanks):
        self._update_target(tanks)
        self._update_speed()
        self._update_image_rotation()
        self._update_pos()
        self._update_fadein_fadeout(speedup_when_fadein=2)
        self.hpbar.update(self.hp, self.max_hp, self.pos, self.image_key)

class Squareship(Trigonship):
    def __init__(self, pos, degs):
        super().__init__(pos, degs)

        self.max_hp = 4
        self.hp = self.max_hp

        self.image_key = "squareship"
        self.image = MATERIALS[self.image_key]

    def _update_speed(self):
        # 旋轉角度(https://stackoverflow.com/questions/10473930/how-do-i-find-the-angle-between-2-points-in-pygame)
        # 注意遊戲座標與常用座標不同(Y軸相反)使用時須加上負號
        dx, dy = self.target.pos - self.pos
        self.image_degs = math.degrees(math.atan2(-dy, dx))
        
        self.speed.update(4, 0)
        self.speed.rotate_ip(-self.image_degs)

class Pentagonship(Trigonship):
    def __init__(self, pos, degs):
        super().__init__(pos, degs)

        self.max_hp = 6
        self.hp = self.max_hp

        self.image_key = "pentagonship"
        self.image = MATERIALS[self.image_key]

    def _update_speed(self):
        # 旋轉角度(https://stackoverflow.com/questions/10473930/how-do-i-find-the-angle-between-2-points-in-pygame)
        # 注意遊戲座標與常用座標不同(Y軸相反)使用時須加上負號
        dx, dy = self.target.pos - self.pos
        self.image_degs = math.degrees(math.atan2(-dy, dx))
        
        self.speed.update(5, 0)
        self.speed.rotate_ip(-self.image_degs)

class Mothership(Trigonship):
    def __init__(self, maxnum_of_littleships):
        pygame.sprite.Sprite.__init__(self)

        self.max_hp = 5000
        self.hp = self.max_hp
        self.damage = 99999

        # 在非緩速區隨機初始位置
        pos = [random.randint(SIZE_OF_SLOWZONE, SIZE_OF_BATTLEFIELD-SIZE_OF_SLOWZONE) for _ in range(2)]
        self.pos = pygame.math.Vector2(pos)
        
        self.speed = pygame.math.Vector2(0, 0)
        
        self.search_time = 20000
        # 設為負數使一開始就搜尋
        self.time_of_starting_to_search = -self.search_time

        self.maxnum_of_littleships = maxnum_of_littleships
        self.littleships = pygame.sprite.Group()
        self.is_reloading = False # 主要用於計算砲管伸縮長度
        self.time_of_starting_to_reload = 0
        self.reload_time = 300
        self.is_cooling = False # 主要用於計算攻擊時機
        self.time_of_starting_to_cool = 0
        self.max_cooldown_time = 5000
        self.cooldown_time = self.max_cooldown_time

        self.time_of_birth = pygame.time.get_ticks()
        self.image_series = "mothership"
        self.image_key = f"{self.image_series}-1.0"
        self.image = MATERIALS[self.image_key]
        self.image_alpha = 0
        self.image_degs = 0
        self.image_scale = 1
        
        self.rect = self.image.get_rect(center=self.pos)

        self.hpbar = pygame.sprite.GroupSingle(Hpbar(self.image_key))

    def _update_speed(self):
        dx, dy = self.target.pos - self.pos
        degs = math.degrees(math.atan2(dy, dx))
        self.speed.update(1, 0)
        self.speed.rotate_ip(degs)
    
    def _update_cooldown_time(self):
        if self.is_cooling:
            elapsed_time = pygame.time.get_ticks() - self.time_of_starting_to_cool
            # 若冷卻時間已過
            if elapsed_time > self.cooldown_time:
                self.is_cooling = False
                # 縮短冷卻時間
                self.cooldown_time -= 5
    
    def _update_reload_time_and_image_key(self):
        # 若發射後的冷卻期間伸縮砲管
        if self.is_reloading:
            # 從發射後所經過的時間
            elapsed_time = pygame.time.get_ticks() - self.time_of_starting_to_reload
            # 冷卻結束
            if elapsed_time >= self.reload_time:
                self.is_reloading = False
            
            # 後25%的時間拉長 有反方向的後座力
            elif elapsed_time > self.reload_time*0.5:
                self.image_key = f"{self.image_series}-1.0"

                if hasattr(self, "recoil"):
                    self.speed += self.recoil.rotate(180-self.image_degs)
            
            elif elapsed_time > self.reload_time*0.45:
                self.image_key = f"{self.image_series}-0.96"
            
            elif elapsed_time > self.reload_time*0.4:
                self.image_key = f"{self.image_series}-0.92"
            
            elif elapsed_time > self.reload_time*0.35:
                self.image_key = f"{self.image_series}-0.88"
            
            elif elapsed_time > self.reload_time*0.3:
                self.image_key = f"{self.image_series}-0.84"
            
            # 前25%的時間收縮
            elif elapsed_time > self.reload_time*0.25:
                self.image_key = f"{self.image_series}-0.84"
            
            elif elapsed_time > self.reload_time*0.2:
                self.image_key = f"{self.image_series}-0.88"
            
            elif elapsed_time > self.reload_time*0.15:
                self.image_key = f"{self.image_series}-0.92"
            
            elif elapsed_time > self.reload_time*0.1:
                self.image_key = f"{self.image_series}-0.96"
            
            elif elapsed_time > self.reload_time*0.05:
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
        if (not self.is_reloading) and (not self.is_cooling) and (self.maxnum_of_littleships > len(self.littleships)):
            self.is_reloading = True
            self.is_cooling = True
            self.time_of_starting_to_reload = pygame.time.get_ticks()
            self.time_of_starting_to_cool = pygame.time.get_ticks()
            
            for degs in range(0, 360, 360//12):
                # 隨著冷卻時間縮短 發射的小飛機種類越強
                p = random.randint(0, self.max_cooldown_time)
                if p < self.cooldown_time:
                    littleship_type = Trigonship
                
                elif p < self.cooldown_time*2:
                    littleship_type = Squareship

                else:
                    littleship_type = Pentagonship
                
                littleship = littleship_type(self.pos, self.image_degs+degs)
                self.littleships.add(littleship)

        self._update_cooldown_time()
        self._update_reload_time_and_image_key()
        self._update_target(tanks)
        self._update_speed()
        self._update_image_rotation()
        self._update_pos()
        self._update_fadein_fadeout()
        self.littleships.update(tanks)
        self.hpbar.update(self.hp, self.max_hp, self.pos, self.image_key)

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
                    collied_tank.skill_pnt[0] += 1
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

        # 初始化能力值面板
        self.num_of_barrel_label = SkillPanelLabel("Barrel", (50,800), pygame.K_1)
        self.reload_time_label = SkillPanelLabel("Reload Time", (50,850), pygame.K_2)
        self.bullet_damage_label = SkillPanelLabel("Bullet Damage", (50,900), pygame.K_3)
        self.bullet_speed_label = SkillPanelLabel("Bullet Speed", (50,950), pygame.K_4)
        self.max_speed_label = SkillPanelLabel("Movement Speed", (50,1000), pygame.K_5)
        self.skill_panel = pygame.sprite.Group()
        self.skill_panel.add(self.num_of_barrel_label)
        self.skill_panel.add(self.reload_time_label)
        self.skill_panel.add(self.bullet_damage_label)
        self.skill_panel.add(self.bullet_speed_label)
        self.skill_panel.add(self.max_speed_label)

        # 初始化能力值點數 以列表儲存為了傳址
        self.skill_pnt = [8]

        self.max_hp = 20
        self.hp = self.max_hp
        self.damage = 10

        # 在非緩速區隨機初始位置
        pos = [random.randint(SIZE_OF_SLOWZONE, SIZE_OF_BATTLEFIELD-SIZE_OF_SLOWZONE) for _ in range(2)]
        self.pos = pygame.math.Vector2(pos)

        self.speed = pygame.math.Vector2(0, 0)
        self.acc = 0.2
        self.recoil = pygame.math.Vector2(0.01, 0)
        
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

        self.hpbar = pygame.sprite.GroupSingle(Hpbar(self.image_key))

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

                    if self.hp <= 0:
                        self._reborn()

            # 偵測小飛機碰撞
            for mothership in motherships:
                collied_littleships = pygame.sprite.spritecollide(self, mothership.littleships, False, pygame.sprite.collide_mask)
                for collied_littleship in collied_littleships:
                    if collied_littleship.hp > 0:
                        # 互相傷害
                        collied_littleship.hp -= self.damage
                        self.hp -= collied_littleship.damage

                        if self.hp <= 0:
                            self._reborn()

    def _update_cam(self):
        # 使鏡頭平滑移動 數字越小鏡頭移動越慢
        self.cam_pos += (self.pos-self.cam_pos) * 0.03
        self.cam.center = self.cam_pos

        # 限制鏡頭邊界
        self.cam.x = min(max(self.cam.x, 0), SIZE_OF_BATTLEFIELD-self.cam.w)
        self.cam.y = min(max(self.cam.y, 0), SIZE_OF_BATTLEFIELD-self.cam.h)
        
    def _reborn(self):
        """若死亡則清除能力值復活"""
        
        # 恢復血量
        self.hp = self.max_hp

        # 清除能力值
        self.skill_pnt[0] = 0
        for label in self.skill_panel:
            label.lv = 0

        pos = [random.randint(SIZE_OF_SLOWZONE, SIZE_OF_BATTLEFIELD-SIZE_OF_SLOWZONE) for _ in range(2)]
        self.pos = pygame.math.Vector2(pos)
    
    def update(self, events, motherships):
        # 伺服器用 根據地址取得該坦克的輸入事件
        if type(events) == dict:
            event = events[self.addr]
        else:
            event = events

        pressed_keys, is_clicked, mouse_pos = event
        # 加上鏡頭位置的偏移
        mouse_pos += pygame.math.Vector2(self.cam.topleft)

        # 顯示或隱藏能力值面板
        if self.skill_pnt[0] > 0:
            for label in self.skill_panel:
                label.image_alpha = 255
        else:
            for label in self.skill_panel:
                label.image_alpha = 0

        # 更新能力值
        self.num_of_barrel = self.num_of_barrel_label.lv + 1
        self.reload_time = 300 - self.reload_time_label.lv * 50
        self.bullet_damage = 1 + self.bullet_damage_label.lv
        self.bullet_speed = 2.5 + self.bullet_speed_label.lv * 0.5
        self.max_speed = 3 + self.max_speed_label.lv * 0.5
        
        # 左鍵發射子彈
        if (not self.is_reloading) and is_clicked:
            self.is_reloading = True
            self.time_of_starting_to_reload = pygame.time.get_ticks()
            if self.num_of_barrel:
                bullet = Bullet(self.color, self.pos, self.image_degs, self.bullet_damage, self.bullet_speed)
                self.bullets.add(bullet)

        self._update_reload_time_and_image_key()
        self._update_speed(pressed_keys)
        self._update_image_rotation(mouse_pos)
        self._update_pos()
        self._update_collision(motherships)
        self._update_fadein_fadeout()
        self._update_cam()
        self.bullets.update(motherships)
        self.skill_panel.update(pressed_keys, self.cam.topleft, self.skill_pnt)
        self.hpbar.update(self.hp, self.max_hp, self.pos, self.image_key)

class Hpbar(pygame.sprite.Sprite):
    def __init__(self, image_key):
        super().__init__()

        self.image_key = "hpbar-0"
        self.image = MATERIALS[self.image_key]

        self.rect = self.image.get_rect()
        self.y_offset = MATERIALS[image_key].get_height() // 2

    def update(self, hp, max_hp, pos, image_key):
        i = 50
        if hp == 0:
            i = 0
        
        # 若有受傷
        else:
            # 保證血量不是負數
            hp = 0 if hp < 0 else hp
            # 兩範圍間的映射
            i = int(50 * hp / max_hp)
            # 取偶數
            if i % 2:
                i -= 1

        self.image_key = f"hpbar-{i}"
        self.image = MATERIALS[self.image_key]
        
        self.rect.center = pos
        self.rect.y += self.y_offset
        
class StartMenuLabel(pygame.sprite.Sprite):
    def __init__(self, text, topleft, clickable=False):
        super().__init__()

        self.text = text
        
        self.clickable = clickable
        self.is_clicked = False

        self.image = MATERIALS[self.text]

        self.rect = self.image.get_rect(topleft=topleft)

    def update(self, event):
        if self.clickable:
            _, is_clicked, mouse_pos = event

            # 檢查滑鼠是否在上
            if self.rect.collidepoint(mouse_pos):
                self.image = MATERIALS[f"mouseon-{self.text}"]
                if is_clicked:
                    self.is_clicked = True
            else:
                self.image = MATERIALS[self.text]

class SkillPanelLabel(pygame.sprite.Sprite):
    def __init__(self, text, topleft, hotkey):
        super().__init__()

        self.lv = 0

        self.x_offset = topleft[0]
        self.y_offset = topleft[1]

        self.text = text
        self.image_key = f"{self.text}-0"
        self.image = MATERIALS[self.image_key]
        self.image_alpha = 0
        
        self.rect = self.image.get_rect()
        
        self.hotkey = hotkey

    def update(self, pressed_keys, cam_topleft, skill_pnt):
        # 座標每次皆重置 為鏡頭座標加上螢幕的相對座標
        self.rect.topleft = cam_topleft
        self.rect.x += self.x_offset
        self.rect.y += self.y_offset

        if pressed_keys[self.hotkey] and skill_pnt[0] and self.lv < 5:
            self.lv += 1
            skill_pnt[0] -= 1

        self.image_key = f"{self.text}-{self.lv}"
        self.image = MATERIALS[self.image_key]
        self.image.set_alpha(self.image_alpha)

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

        # 載入起始選單
        MATERIALS["Die"] = pygame.image.load(f"materials/Die.png")
        MATERIALS["py"] = pygame.image.load(f"materials/py.png")
        MATERIALS["Play"] = pygame.image.load(f"materials/Play.png")
        MATERIALS["New"] = pygame.image.load(f"materials/New.png")
        MATERIALS["Connect"] = pygame.image.load(f"materials/Connect.png")
        MATERIALS["mouseon-Play"] = pygame.image.load(f"materials/mouseon-Play.png")
        MATERIALS["mouseon-New"] = pygame.image.load(f"materials/mouseon-New.png")
        MATERIALS["mouseon-Connect"] = pygame.image.load(f"materials/mouseon-Connect.png")
        
        # 建立起始選單
        self.single_label = StartMenuLabel("Play", (800,500), True)
        self.server_label = StartMenuLabel("New", (800,600), True)
        self.client_label = StartMenuLabel("Connect", (800,700), True)
        self.start_menu = pygame.sprite.RenderUpdates()
        self.start_menu.add(StartMenuLabel("Die", (800,200)))
        self.start_menu.add(StartMenuLabel("py", (1010,200)))
        self.start_menu.add(self.single_label)
        self.start_menu.add(self.server_label)
        self.start_menu.add(self.client_label)

    def select_mode(self):
        self.display.fill((240, 240, 240))
        pygame.display.update()

        self.mode = None
        while self.is_running and not self.mode:
            event = self.get_event()
            self.start_menu.update(event)

            changes = self.start_menu.draw(self.display)
            self.clock.tick(144)
            pygame.display.update(changes)

            if self.single_label.is_clicked:
                self.mode = "single"
            elif self.server_label.is_clicked:
                self.mode = "server"
            elif self.client_label.is_clicked:
                self.mode = "client"

    def add_tank(self, addr=None, serverself=False):
        if self.mode == "server":
            # 分配顏色
            color = random.choice(self.remaining_color)
            self.remaining_color.remove(color)

            tank = Tank(color, addr)
            self.tanks.add(tank)

            if serverself:
                self.serverself_cam = tank.cam
                self.serverself_skill_panel = tank.skill_panel
        
        # 單人模式用
        else:
            # 初始化坦克
            tank = Tank("blue")
            self.tanks.add(tank)

    def add_mothership(self):
        """加入母艦 數量與客戶端人數相同"""

        maxnum_of_littleships = 50 / len(self.tanks)

        for _ in range(len(self.tanks)):
            mothership = Mothership(maxnum_of_littleships)
            self.motherships.add(mothership)

    def add_cross(self):
        """加入升級十字 產生機率根據客戶端人數遞增"""

        # 限制總數量
        if len(self.crosses) < 10:
            max_ = 500 // len(self.tanks)
            # 只有選中是0時才增加
            if not random.randint(0, max_):
                self.crosses.add(Cross())

    def get_event(self):
        """取得該客戶端的輸入事件"""

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

    def get_sprites(self):
        """伺服器用於取得所有精靈的繪製資訊 若完全透明則不傳送"""
        
        sprites = []

        for tank in self.tanks:
            key = tank.image_key
            rect = tank.rect
            topleft = tank.rect.topleft
            alpha = tank.image_alpha
            degs = tank.image_degs

            if alpha > 0:
                sprites.append((key, rect, topleft, alpha, degs))

            for bullet in tank.bullets:
                key = bullet.image_key
                rect = bullet.rect
                topleft = bullet.rect.topleft
                alpha = bullet.image_alpha
                degs = 0

                if alpha > 0:
                    sprites.append((key, rect, topleft, alpha, degs))

            key = tank.hpbar.sprite.image_key
            rect = tank.hpbar.sprite.rect
            topleft = tank.hpbar.sprite.rect.topleft
            alpha = 255
            degs = 0
            sprites.append((key, rect, topleft, alpha, degs))

        for mothership in self.motherships:
            key = mothership.image_key
            rect = mothership.rect
            topleft = mothership.rect.topleft
            alpha = mothership.image_alpha
            degs = mothership.image_degs

            if alpha > 0:
                sprites.append((key, rect, topleft, alpha, degs))

            for littleship in mothership.littleships:
                key = littleship.image_key
                rect = littleship.rect
                topleft = littleship.rect.topleft
                alpha = littleship.image_alpha
                degs = littleship.image_degs

                if alpha > 0:
                    sprites.append((key, rect, topleft, alpha, degs))
    
        return sprites

    def get_skill_panels(self):
        """伺服器用於取得所有客戶端能力值面板的繪製資訊 若無可用點數則不傳送"""

        skill_panels = {}

        for tank in self.tanks:
            skill_panels[tank.addr] = []
            if tank.skill_pnt:
                for label in tank.skill_panel:
                    key = label.image_key
                    rect = label.rect
                    topleft = label.rect.topleft

                    skill_panels[tank.addr].append((key, rect, topleft))

            else:
                skill_panels[tank.addr] = None
        
        return skill_panels
    
    def get_cams(self):
        """伺服器用於取得每個客戶端鏡頭位置"""

        cams = {}
        for tank in self.tanks:
            cams[tank.addr] = tank.cam
        return cams
    
    def update_screen(self, sprites=None, skill_panel=None, cam=None):
        """更新畫面 先畫出來再以鏡頭位置切割戰場出顯示所需部分"""
        
        if self.mode == "client":
            # 畫所有精靈
            for key, rect, topleft, alpha, degs in sprites:
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
                
                # 若圖片無調整則使用原圖畫
                if no_transform:
                    image = MATERIALS[key]

                # 設定透明度
                image.set_alpha(alpha)

                # 畫該精靈在戰場上
                MATERIALS["battlefield"].blit(image, topleft)
            
            # 畫能力值面板
            if skill_panel:
                for key, _, topleft in skill_panel:
                    image = MATERIALS[key]
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

            # 畫坦克血條
            for tank in self.tanks:
                tank.hpbar.draw(MATERIALS["battlefield"])
            
            # 畫母艦血條
            for mothership in self.motherships:
                mothership.hpbar.draw(MATERIALS["battlefield"])

            # 畫小飛機血條
            for mothership in self.motherships:
                for littleship in mothership.littleships:
                    littleship.hpbar.draw(MATERIALS["battlefield"])
            

            if self.mode == "server":
                # 畫能力值面板
                self.serverself_skill_panel.draw(MATERIALS["battlefield"])

                # 更新鏡頭位置
                cam = self.serverself_cam
            
            # 單人模式用
            else:
                # 畫能力值面板
                for tank in self.tanks:
                    tank.skill_panel.draw(MATERIALS["battlefield"])

                # 更新鏡頭位置
                cam = self.tanks.sprites()[0].cam

        # 將鏡頭中的戰場更新到畫面上
        self.display.blit(MATERIALS["battlefield"], (0,0), cam)
        self.clock.tick(60)
        pygame.display.update()

        if self.mode == "client":
            # 清所有精靈
            for _, rect, topleft, _, _ in sprites:
                MATERIALS["battlefield"].blit(MATERIALS["background"], topleft, rect)

            # 清能力值面板
            if skill_panel:
                for key, rect, topleft in skill_panel:
                    image = MATERIALS[key]
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
           
            # 清坦克血條
            for tank in self.tanks:
                tank.hpbar.clear(MATERIALS["battlefield"], MATERIALS["background"])

            # 清母艦血條
            for mothership in self.motherships:
                mothership.hpbar.clear(MATERIALS["battlefield"], MATERIALS["background"])

            # 清小飛機血條
            for mothership in self.motherships:
                for littleship in mothership.littleships:
                    littleship.hpbar.clear(MATERIALS["battlefield"], MATERIALS["background"])

            if self.mode == "server":
                # 清能力值面板
                self.serverself_skill_panel.clear(MATERIALS["battlefield"], MATERIALS["background"])
            
            # 單人模式用
            else:
                # 清能力值面板
                for tank in self.tanks:
                    tank.skill_panel.clear(MATERIALS["battlefield"], MATERIALS["background"])