from math import atan2, degrees, pi, sin, cos
from random import randrange

import pygame
import pygame.gfxdraw
from pygame.locals import *

from config import *


class ExpSquare(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.exp = 5
        self.hp = 3
        self.max_hp = 3
        self.damage = 5

        self.degree = randrange(360)
        self.speed = pygame.math.Vector2(0.01, 0).rotate(self.degree)
        x, y = randrange(screen.get_width()), randrange(screen.get_height())
        self.pos = pygame.math.Vector2(x, y)

        self.image_orig = pygame.Surface((35, 35)).convert()
        pygame.gfxdraw.box(self.image_orig, (0, 0, 35, 35), DARK_YELLOW)
        pygame.gfxdraw.box(self.image_orig, (3, 3, 29, 29), YELLOW)
        self.image_orig.set_colorkey(BLACK)
        self.image_alpha = 254
        self.image_scale = (self.image_orig.get_width(), self.image_orig.get_height())

    def _check_moving(self):
        self.image = pygame.transform.rotate(self.image_orig, self.degree)
        self.degree = (self.degree+0.03) % 360
        self.mask = pygame.mask.from_surface(self.image)
        self.pos += self.speed
        self.rect = self.image.get_rect(center=self.pos)
        
    def _check_hp(self):
        # 死亡動畫
        if self.hp <= 0:
            # 消失時放大
            self.image = pygame.transform.scale(self.image, self.image_scale)
            self.image_scale = int(self.image_scale[0]*1.03), int(self.image_scale[1]*1.03)
            self.rect = self.image.get_rect(center=self.pos)
            # 消失時淡出
            self.image.set_alpha(self.image_alpha)
            self.image_alpha -= 8
            # 完全淡出後移除
            if self.image_alpha < 0:
                self.kill()
        # 顯示血量
        elif self.hp < self.max_hp:
            # 新建加長的畫布
            new_image = pygame.Surface((self.image.get_width(), self.image.get_height()+15), SRCALPHA)
            # 在上方先畫上原本的
            new_image.blit(self.image, (0,0))
            # 再畫上血條
            x, y, w, h = (self.image.get_width()-self.image_orig.get_width())/2, self.image.get_height()+7, self.image_orig.get_width(), 7
            pygame.gfxdraw.box(new_image, (x, y, w, h), DARK_GRAY)
            boarder = 2
            x += boarder
            y += boarder
            w *= self.hp/self.max_hp
            w -=boarder*2
            h -= boarder*2
            pygame.gfxdraw.box(new_image, (x, y, w, h), HP_COLOR)
            
            self.image = new_image
            self.rect.height +=7
    
    def update(self):
        self._check_moving()
        self._check_hp()

class SmallBullet(pygame.sprite.Sprite):
    def __init__(self, bullet_max_hp, bullet_damage, bullet_speed, tank_pos, tank_degree, barrel_width):
        super().__init__()

        self.birth_time = pygame.time.get_ticks()
        
        self.max_hp = bullet_max_hp
        self.hp = self.max_hp
        self.damage = bullet_damage
        self.speed = pygame.math.Vector2(bullet_speed, 0).rotate(-tank_degree)

        # 偏移的方向與彈藥方向相同 長度為砲管的長度
        pos_offset = pygame.math.Vector2(self.speed)
        pos_offset.scale_to_length(barrel_width)
        # 起始位置為砲口
        self.pos = tank_pos + pos_offset

        self.image = pygame.Surface((30, 30)).convert()
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, BLUE, (15, 15), 12, 0)
        pygame.draw.circle(self.image, DARK_BLUE, (15, 15), 12, 3)
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.image_alpha = 254

        # 紀錄剛碰撞的敵人 避免重複檢測
        self.just_collide_enemy = pygame.sprite.Group()

    def _check_moving(self):
        self.pos += self.speed
        self.rect.center = self.pos

    def _check_hp(self):
        # 限制持續時間
        alive_time = pygame.time.get_ticks() - self.birth_time
        if self.hp <= 0 or alive_time > 500:
            # 消失時放大
            scale = int(self.image.get_width()*1.06), int(self.image.get_height()*1.06)
            self.image = pygame.transform.scale(self.image, scale)
            self.rect = self.image.get_rect(center=self.pos)
            # 消失時淡出
            self.image.set_alpha(self.image_alpha)
            self.image_alpha -= 20
            # 完全淡出後移除
            if self.image_alpha < 0:
                self.kill()
    
    # def _check_collide(self):
    #     # 所有命中的敵人
    #     for enemy in pygame.sprite.spritecollide(self, enemy_group, False, pygame.sprite.collide_mask):
    #         can_attack = False if self.just_collide_enemy.has(enemy) else True
    #         if self.hp>0 and enemy.hp>0 and can_attack:
    #             # 互相傷害
    #             self.hp -= enemy.damage
    #             enemy.hp -= self.damage
    #             self.just_collide_enemy.add(enemy)
    #             # 若殺死則得到經驗值
    #             if enemy.hp < 0:
    #                 # self.player_exp += enemy.exp
    
    def update(self, *arg):
        self._check_moving()
        self._check_hp()
        # self._check_collide()

class Tank(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.max_hp = 10
        self.hp_regen = 0.1
        self.damage = 1
        self.acc = 0.03
        self.reloading_time = 500

        self.pos = pygame.math.Vector2(TANK_INIT_POS)
        self.speed = pygame.math.Vector2(0, 0)
        self.max_speed = TANK_MAX_SPEED
        self.recoil = pygame.math.Vector2(TANK_RECOIL, 0)

        self.bullet_type = SmallBullet
        self.barrel_scale = 1
        self.barrel_width = 10
        
        # 用於判斷是否可再攻擊
        self.can_attack = True
        self.attack_time = 0

        self.image = pygame.Surface((100, 100)).convert()
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)

    def _update_image(self, mouse_pos):
        # 旋轉角度(https://stackoverflow.com/questions/10473930/how-do-i-find-the-angle-between-2-points-in-pygame)
        # 注意遊戲的座標與常用座標不同(Y軸相反)使用時須加上負號
        mouse_x, mouse_y = mouse_pos
        dx, dy = mouse_x-self.pos.x, mouse_y-self.pos.y
        self.degree = degrees(atan2(-dy, dx) % (2*pi))
        
        # 清除畫布
        self.image.fill(BLACK)
        
        # 砲管頂點
        # p1(x1,y1)---p4(x2,y1)
        # p2(x1,y2)---p3(x2,y2)
        x1, y1 = 50, 40
        x2, y2 = x1+47*self.barrel_scale, 60
        points = (x1, y1), (x1, y2), (x2, y2), (x2, y1)
        # 旋轉砲管
        points = [(point-(50, 50)).rotate(-self.degree)+(50, 50)
                  for point in map(pygame.math.Vector2, points)]
        pygame.draw.polygon(self.image, GRAY, points, 0)
        pygame.draw.polygon(self.image, DARK_GRAY, points, 3)
        # 本體
        pygame.draw.circle(self.image, BLUE, (50, 50), 25, 0)
        pygame.draw.circle(self.image, DARK_BLUE, (50, 50), 25, 3)

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, pressed_keys, mouse_pos, tank_max_hp, tank_hp_regen, tank_damage, tank_acc, reloading_time):
        # 更新能力值
        self.max_hp = 10 + tank_max_hp
        self.hp_regen = 0.1 + tank_hp_regen
        self.damage = 1 + tank_damage
        self.acc = 0.03 + tank_acc
        self.reloading_time = 500 + reloading_time

        # 檢查是否有加速度
        if pressed_keys[K_w]:
            self.speed += (0, -self.acc)
        elif pressed_keys[K_s]:
            self.speed += (0, self.acc)
        else:
            self.speed.y /= 1.01
            self.speed.y = 0 if abs(self.speed.y) < 0.0000005 else self.speed.y
        if pressed_keys[K_a]:
            self.speed += (-self.acc, 0)
        elif pressed_keys[K_d]:
            self.speed += (self.acc, 0)
        else:
            self.speed.x /= 1.01
            self.speed.x = 0 if abs(self.speed.x) < 0.0000005 else self.speed.x

        # 限制速度在指定區間內
        self.speed.x = min(self.max_speed, max(-self.max_speed, self.speed.x))
        self.speed.y = min(self.max_speed, max(-self.max_speed, self.speed.y))

        # 更新位置
        self.pos += self.speed
        self.rect.center = self.pos

        # 冷卻期間伸縮砲管
        if not self.can_attack:
            # 從攻擊後所經過的時間
            elapsed_time = pygame.time.get_ticks() - self.attack_time
            # 前25%的時間收縮
            if elapsed_time < self.reloading_time*0.25:
                self.barrel_scale -= 0.003
            # 再25%的時間拉長
            elif elapsed_time < self.reloading_time*0.5:
                self.barrel_scale += 0.003
                # 後座力是砲口的反方向
                self.speed += self.recoil.rotate(180-self.degree)
            # 其餘時間將長度恢復原狀
            elif elapsed_time < self.reloading_time:
                self.barrel_scale = 1
            # 冷卻結束
            else:
                self.can_attack = True

        # 由於砲管會收縮因此每次重畫收縮的情況
        self._update_image(mouse_pos)

class player:
    def __init__(self):
        # 玩家的能力值
        self.tank_max_hp = 0
        self.tank_hp_regen = 0
        self.tank_damage = 0
        self.tank_acc = 0
        self.reloading_time = 0
        self.bullet_max_hp = 5
        self.bullet_damage = 1
        self.bullet_speed = 4

        self.player_exp = 0

        self.tank = Tank()
        self.group = pygame.sprite.Group()
        self.group.add(self.tank)

    def update(self):
        # 按左鍵攻擊時將子彈加入群組
        is_click = pygame.mouse.get_pressed()[0]
        if is_click and self.tank.can_attack:
            self.tank.can_attack = False
            self.tank.attack_time = pygame.time.get_ticks()
            bullet = self.tank.bullet_type(self.bullet_max_hp, self.bullet_damage, self.bullet_speed, self.tank.pos, self.tank.degree, self.tank.barrel_width)
            self.group.add(bullet)

        pressed_keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        self.group.update(pressed_keys, mouse_pos, self.tank_max_hp, self.tank_hp_regen, self.tank_damage, self.tank_acc, self.reloading_time)

    def draw(self, screen):
        self.group.draw(screen)

pygame.init()
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)
pygame.display.set_caption("Diepy")
screen = pygame.display.set_mode((1920, 1080))

# 建立時鐘限制幀率
clock = pygame.time.Clock()
# 玩家列表 順序代表第幾位
players = [player()]
# 敵人列表 包含經驗塊
enemy_group = pygame.sprite.Group()

is_running = True
while is_running:
    # 關閉遊戲
    for event in pygame.event.get():
        if event.type == QUIT:
            is_running = False
    # 清除畫面
    screen.fill(BG_COLOR)
    # 生成經驗磚
    if len(enemy_group) < 50:
        enemy_group.add(ExpSquare())

    enemy_group.update()
    enemy_group.draw(screen)
    for player in players:
        player.update()
        player.draw(screen)

    pygame.display.update()

    # 設定每秒144幀
    clock.tick(144)

pygame.quit()
# sys.exit()
