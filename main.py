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
        self.hp = 5
        self.damage = 1

        # 隨機移動
        degree = randrange(360)
        self.speed = pygame.math.Vector2(0.03, 0).rotate(degree)
        x, y = randrange(screen.get_width()), randrange(screen.get_height())
        self.pos = pygame.math.Vector2(x, y)
        self.rot_speed = 1

    def _draw(self):
        self.image = pygame.Surface((35, 35), SRCALPHA).convert()
        pygame.draw.rect(self.image, YELLOW, (0, 0, 35, 35), 0)
        pygame.draw.rect(self.image, DARK_YELLOW, (1, 1, 33, 33), 3)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self._draw()
        self.pos += self.speed
        self.rect = self.image.get_rect(center=self.pos)


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

        self.image = pygame.Surface((30, 30)).convert()
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, BLUE, (15, 15), 12, 0)
        pygame.draw.circle(self.image, DARK_BLUE, (15, 15), 12, 3)
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.image_alpha = 254

    def _check_moving(self):
        self.pos += self.speed
        self.rect = self.image.get_rect(center=self.pos)

    def _check_alive(self):
        pass
        
    def update(self):
        self._check_moving()
        self._check_alive()
        # 限制持續時間
        alive_time = pygame.time.get_ticks() - self.birth_time
        if alive_time > 500:
            # 消失時放大
            scale = int(self.image.get_width() *
                        1.06), int(self.image.get_height()*1.06)
            self.image = pygame.transform.scale(self.image, scale)
            # 消失時淡出
            self.image.set_alpha(self.image_alpha)
            self.image_alpha -= 20
            # 完全淡出後移除
            if self.image_alpha < 0:
                self.kill()

class Tank(pygame.sprite.Sprite):
    def __init__(self, ammunition_group):
        super().__init__()

        self.hp = 50
        self.ammunition_group = ammunition_group

        self.pos = pygame.math.Vector2(500, 500)
        self.acc = TANK_ACC
        self.max_speed = TANK_MAX_SPEED

        self.order_of_firing = (
            {"type": Bullet, "degree_offset": 0, "barrel_width": 50}, ),
        self.order_of_firing_index = 0
        self.can_fire = True
        self.fire_time = 0
        self.barrel_scale = 1
        self.recoil = pygame.math.Vector2(0.015, 0)

        self.image = pygame.Surface((100, 100)).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

    def _check_ability(self, hp_regen, max_hp, body_damage, bullet_speed, bullet_hp, bullet_damage, reloading_time, speed):
        self.hp_regen = hp_regen
        self.max_hp = max_hp
        self.damage = body_damage
        self.bullet_speed = bullet_speed
        self.bullet_hp = bullet_hp
        self.bullet_damage = bullet_damage
        self.reloading_time = reloading_time
        self.speed = speed

    def _check_moving(self, pressed_keys):
        # 檢查是否有加速度
        is_pressed = True

        # 移動
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
        self.rect.center = self.pos

    def _check_firing(self, mouse_x, mouse_y, is_click):
        # 計算旋轉角度(https://stackoverflow.com/questions/10473930/how-do-i-find-the-angle-between-2-points-in-pygame)
        dx, dy = mouse_x-self.pos.x, mouse_y-self.pos.y
        self.degree = degrees(atan2(-dy, dx) % (2*pi))

        # 按左鍵發射子彈
        if is_click and self.can_fire:
            self.can_fire = False
            self.fire_time = pygame.time.get_ticks()

            # 依子彈順序發射
            for each in self.order_of_firing[self.order_of_firing_index]:
                ammunition = each["type"](
                    self.bullet_speed.rotate(-self.degree +
                                             each["degree_offset"]),
                    self.bullet_hp,
                    self.bullet_damage,
                    self.pos,
                    each["barrel_width"])
                self.ammunition_group.add(ammunition)

            # 換下一組
            self.order_of_firing_index += 1
            self.order_of_firing_index %= len(self.order_of_firing)

        # 判斷能否再發射
        if not self.can_fire:
            # 從發射後所經過的時間
            elapsed_time = pygame.time.get_ticks() - self.fire_time
            # 前25%的時間收縮
            if elapsed_time < self.reloading_time*0.25:
                self.barrel_scale -= 0.005
            # 再25%的時間拉長
            elif elapsed_time < self.reloading_time*0.5:
                self.barrel_scale += 0.005
                # 後座力是砲口的反方向
                self.speed += self.recoil.rotate(180-self.degree)
            # 其餘時間將長度恢復原狀
            elif elapsed_time < self.reloading_time:
                self.barrel_scale = 1
            # 冷卻時間結束
            else:
                self.can_fire = True

    # 更新外觀
    def _draw(self):
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

    def update(self, hp_regen, max_hp, body_damage, bullet_speed, bullet_hp, bullet_damage, reloading_time, speed, pressed_keys, mouse_x, mouse_y, is_click):
        self._check_ability(hp_regen, max_hp, body_damage, bullet_speed,
                            bullet_hp, bullet_damage, reloading_time, speed)
        self._check_moving(pressed_keys)
        self._check_firing(mouse_x, mouse_y, is_click)
        self._draw()

class player:
    def __init__(self):
        self.exp = 0

        self.hp_regen = 3
        self.max_hp = 100
        self.body_damage = 10
        self.bullet_speed = pygame.math.Vector2(4, 0)
        self.bullet_hp = 100
        self.bullet_damage = 10
        self.reloading_time = 500
        self.speed = pygame.math.Vector2(0, 0)

        # 存放子彈
        self.ammunition_group = pygame.sprite.Group()
        # 存放本體
        self.tank_group = pygame.sprite.GroupSingle()
        # 傳入子彈群組參數用於發射時存放
        self.tank_group.add(Tank(self.ammunition_group))

    def update(self):
        # 更新本體
        pressed_keys = pygame.key.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_click = pygame.mouse.get_pressed()[0]
        self.tank_group.update(self.hp_regen, self.max_hp, self.body_damage, self.bullet_speed, self.bullet_hp,
                               self.bullet_damage, self.reloading_time, self.speed, pressed_keys, mouse_x, mouse_y, is_click)
        # 更新子彈
        self.ammunition_group.update()

    def draw(self, screen):
        self.tank_group.draw(screen)
        self.ammunition_group.draw(screen)


pygame.init()
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Diepy.")

# 建立時鐘限制幀率
clock = pygame.time.Clock()
# 玩家列表 順序代表第幾位
players = [player()]
# 敵人列表 包含經驗塊
enemy = pygame.sprite.Group()

is_running = True
while is_running:
    # 關閉遊戲
    for event in pygame.event.get():
        if event.type == QUIT:
            is_running = False
    # 清除畫面
    screen.fill(BG_COLOR)
    # 生成經驗磚
    if len(enemy) < 50:
        enemy.add(ExpSquare())

    enemy.update()
    enemy.draw(screen)
    for player in players:
        player.update()
        player.draw(screen)

        # 碰撞檢測
        # 該玩家所有的子彈和本體
        for ammunition in player.ammunition_group:
            # 該玩家所有命中的經驗塊
            for expblock in pygame.sprite.spritecollide(ammunition, enemy, dokill=False):
                # 互相傷害
                ammunition.hp -= expblock.damage
                expblock.hp -= ammunition.damage

                if expblock.hp < 0:
                    player.exp += expblock.exp

    pygame.display.update()

    # 設定每秒144幀
    clock.tick(144)

pygame.quit()
# sys.exit()
