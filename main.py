from math import atan2, degrees, pi, sin, cos

import pygame
from pygame.locals import *

from config import *


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, degree):
        super().__init__()

        # 外觀
        self.image = pygame.Surface(
            BULLET_SURFACE_SIZE, SRCALPHA).convert_alpha()
        pygame.draw.circle(self.image, LIGHT_BLUE,
                           BULLET_CENTER, BULLET_SIZE, 0)
        pygame.draw.circle(self.image, BLUE, BULLET_CENTER, BULLET_SIZE, 3)

        self.speed = pygame.math.Vector2(5, 0).rotate(-degree)
        # 位移方向與速度相同並放大至緊貼砲口的位置
        self.offset = pygame.math.Vector2(self.speed)
        self.offset.scale_to_length(TANK_BARREL_W-BULLET_SIZE)
        # 發射位置為坦克中心加上位移
        self.pos = pygame.math.Vector2(pos) + self.offset
        self.rect = self.image.get_rect(center=self.pos)
        self.birth_time = pygame.time.get_ticks()

    def update(self):
        # 限制持續時間
        alive_time = pygame.time.get_ticks() - self.birth_time
        if alive_time >= 1000:
            self.kill()
        
        self.pos += self.speed

    # def draw(self, screen):
        self.rect = self.image.get_rect(center=self.pos)
        # screen.blit(self.image, self.rect)


class Tank(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.hp_regen = 3
        self.max_hp = 100
        self.body_damage = 10
        self.bullet_speed = 1
        self.bullet_hp = 100
        self.bullet_damage = 10
        self.reloading_time = 500
        self.speed = pygame.math.Vector2(0, 0)

        self.pos = pygame.math.Vector2(100, 100)
        self.acc = TANK_ACC
        self.max_speed = TANK_MAX_SPEED

        self.can_fire = True
        self.elapsed_time = 0
        self.barrel_scale = 1
        self.recoil = pygame.math.Vector2(0.02, 0)
        self.use_autofire = False
    
    # 更新位置
    def move(self):
        # 檢查是否有加速度
        is_pressed = True

        # 上下左右移動
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_w]:
            self.speed += (0, -self.acc)
            is_pressed = False
        if pressed_keys[K_s]:
            self.speed += (0, self.acc)
            is_pressed = False
        if pressed_keys[K_a]:
            self.speed += (-self.acc, 0)
            is_pressed = False
        if pressed_keys[K_d]:
            self.speed += (self.acc, 0)
            is_pressed = False

        # 若沒有加速度則減速到靜止
        if is_pressed:
            self.speed.x /= 1.03
            self.speed.y /= 1.03
            self.speed.x = 0 if abs(self.speed.x) < 0.0000001 else self.speed.x
            self.speed.y = 0 if abs(self.speed.y) < 0.0000001 else self.speed.y

        # 限制速度在指定區間內
        self.speed.x = min(self.max_speed, max(-self.max_speed, self.speed.x))
        self.speed.y = min(self.max_speed, max(-self.max_speed, self.speed.y))

        self.pos += self.speed
    
    # 更新發射
    def fire(self):
        # 計算砲管角度(https://stackoverflow.com/questions/10473930/how-do-i-find-the-angle-between-2-points-in-pygame)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx, dy = mouse_x-self.pos.x, mouse_y-self.pos.y
        self.degree = degrees(atan2(-dy, dx) % (2*pi))

        # 左鍵發射子彈
        is_click = pygame.mouse.get_pressed()[0]
        if is_click and self.can_fire:
            # 建立子彈
            if isinstance(self, Tank):
                bullet = Bullet(self.pos, self.degree)
                player1.add(bullet)

            self.can_fire = False
            self.fire_time = pygame.time.get_ticks()
        
        # 子彈發射一輪後 進入冷卻且期間伸縮砲管
        if not self.can_fire:
            # 從發射後經過多少的時間
            self.elapsed_time = pygame.time.get_ticks() - self.fire_time
            # 前25%的時間收縮
            if self.elapsed_time < self.reloading_time*0.25:
                self.barrel_scale -= 0.01
                # 後座力是砲口的反方向
                self.speed += self.recoil.rotate(180-self.degree)
            # 再5%的時間拉長
            elif self.elapsed_time < self.reloading_time*0.5:
                self.barrel_scale += 0.01
                # 後座力是砲口的反方向
                self.speed += self.recoil.rotate(180-self.degree)
            # 判斷子彈是否重裝完成
            elif self.elapsed_time >= self.reloading_time:
                self.can_fire = True
            # 確保長度恢復原狀
            else:
                self.barrel_scale = 1

    # 更新外觀
    def draw(self):
        # 建立透明畫布
        self.image = pygame.Surface(
            TANK_SURFACE_SIZE, SRCALPHA).convert_alpha()
        # 砲管
        pygame.draw.rect(self.image, LIGHT_GRAY, (TANK_BARREL_X, TANK_BARREL_Y,
                                                  TANK_BARREL_W*self.barrel_scale, TANK_BARREL_H), 0)
        pygame.draw.rect(self.image, GRAY, (TANK_BARREL_X, TANK_BARREL_Y,
                                            TANK_BARREL_W*self.barrel_scale, TANK_BARREL_H), 3)
        # 本體
        pygame.draw.circle(self.image, LIGHT_BLUE, TANK_CENTER, TANK_SIZE, 0)
        pygame.draw.circle(self.image, BLUE, TANK_CENTER, TANK_SIZE, 3)
        # 旋轉
        self.image = pygame.transform.rotate(self.image, self.degree)
        # 畫在螢幕的指定位置上
        self.rect = self.image.get_rect(center=self.pos)
    
    def update(self):
        self.move()
        self.fire()
        self.draw()
        

pygame.init()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("DIEPy.")

# 建立時鐘限制幀率
clock = pygame.time.Clock()

tank = Tank()
player1 = pygame.sprite.Group()
player1.add(tank)

is_running = True
while is_running:
    # 關閉遊戲
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

    # 清除畫面
    screen.fill(WHITE)

    player1.update()
    # 使用group的draw不是sprite的
    player1.draw(screen)
    pygame.display.update()

    # 設定每秒60幀
    clock.tick(60)

pygame.quit()
# sys.exit()
