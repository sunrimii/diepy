from math import atan2, degrees, pi, sin, cos

import pygame
from pygame.locals import *

from config import *


class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_speed, bullet_hp, bullet_damage, pos, barrel_width):
        super().__init__()
        
        self.birth_time = pygame.time.get_ticks()

        self.speed = bullet_speed
        self.hp = bullet_hp
        self.damage = bullet_damage
        # 偏移的方向與子彈方向相同 長度為砲管的長度
        pos_offset = pygame.math.Vector2(self.speed)
        pos_offset.scale_to_length(barrel_width)
        # 起始位置為砲口
        self.pos = pos + pos_offset
        
        self.image = pygame.Surface((50, 50), SRCALPHA).convert_alpha()
        pygame.draw.circle(self.image, LIGHT_BLUE,(25, 25), 10, 0)
        pygame.draw.circle(self.image, BLUE, (25, 25), 10, 3)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        # 限制持續時間
        alive_time = pygame.time.get_ticks() - self.birth_time
        if alive_time >= 1000:
            self.kill()

        self.pos += self.speed
        self.rect = self.image.get_rect(center=self.pos)


class Tank(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.hp_regen = 3
        self.max_hp = 100
        self.body_damage = 10
        self.bullet_speed = pygame.math.Vector2(5, 0)
        self.bullet_hp = 100
        self.bullet_damage = 10
        self.reloading_time = 500
        self.speed = pygame.math.Vector2(0, 0)

        self.pos = pygame.math.Vector2(100, 100)
        self.acc = TANK_ACC
        self.max_speed = TANK_MAX_SPEED

        self.bullet_order = ({"type":Bullet, "degree_offset":0, "barrel_width":50}, ), 
        self.bullet_order_index = 0
        self.can_fire = True
        self.fire_time = 0
        self.barrel_scale = 1
        self.recoil = pygame.math.Vector2(0.015, 0)
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

        # 若沒有加速度則慢慢減速到靜止
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
        # 計算旋轉角度(https://stackoverflow.com/questions/10473930/how-do-i-find-the-angle-between-2-points-in-pygame)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx, dy = mouse_x-self.pos.x, mouse_y-self.pos.y
        self.degree = degrees(atan2(-dy, dx) % (2*pi))

        # 按左鍵發射子彈
        is_click = pygame.mouse.get_pressed()[0]
        if is_click and self.can_fire:
            self.can_fire = False
            self.fire_time = pygame.time.get_ticks()

            # 依子彈順序發射
            for each in self.bullet_order[self.bullet_order_index]:
                ammunition = each["type"](
                    self.bullet_speed.rotate(-self.degree + each["degree_offset"]),
                    self.bullet_hp,
                    self.bullet_damage,
                    self.pos,
                    each["barrel_width"])
                player1.add(ammunition)

            # 換下一組
            self.bullet_order_index += 1
            self.bullet_order_index %= len(self.bullet_order)

        # 判斷能否再發射
        if not self.can_fire:
            # 從發射後所經過的時間
            elapsed_time = pygame.time.get_ticks() - self.fire_time
            # 前25%的時間收縮
            if elapsed_time < self.reloading_time*0.25:
                self.barrel_scale -= 0.01
            # 再25%的時間拉長
            elif elapsed_time < self.reloading_time*0.5:
                self.barrel_scale += 0.01
                # 後座力是砲口的反方向
                self.speed += self.recoil.rotate(180-self.degree)
            # 其餘時間將長度恢復原狀
            elif elapsed_time < self.reloading_time:
                self.barrel_scale = 1
            # 冷卻時間結束
            else:
                self.can_fire = True

    # 更新外觀
    def draw(self):
        # 建立透明畫布
        self.image = pygame.Surface((100, 100), SRCALPHA).convert_alpha()
        # 砲管頂點
        # p1(x1,y1)---p4(x2,y1)
        # p2(x1,y2)---p3(x2,y2)
        x1, y1 = 50, 40
        x2, y2 = x1+47*self.barrel_scale, 60
        points = (x1,y1), (x1,y2), (x2,y2), (x2,y1)
        # 旋轉砲管
        points = [(point-(50,50)).rotate(-self.degree)+(50,50) for point in map(pygame.math.Vector2, points)]
        pygame.draw.polygon(self.image, LIGHT_GRAY, points, 0)
        pygame.draw.polygon(self.image, GRAY, points, 3)
        # 本體
        pygame.draw.circle(self.image, LIGHT_BLUE, (50,50), 25, 0)
        pygame.draw.circle(self.image, BLUE, (50,50), 25, 3)
        # 指定畫布位置
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
