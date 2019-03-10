from math import atan2, degrees, pi, sin, cos
from random import randrange

import pygame
import pygame.gfxdraw
import pygame.locals

from config import *


class ExpSquare(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.hp = 3
        self.max_hp = 3
        self.damage = 5

        self.degree = randrange(360)
        self.speed = pygame.math.Vector2(0.01, 0).rotate(self.degree)
        x, y = randrange(screen.get_width()), randrange(screen.get_height())
        self.pos = pygame.math.Vector2(x, y)

        self.image_orig = pygame.Surface((35, 35)).convert()
        pygame.gfxdraw.box(self.image_orig, (0, 0, 35, 35), DARK_GRAY)
        pygame.gfxdraw.box(self.image_orig, (3, 3, 29, 29), GRAY)
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
            new_image = pygame.Surface((self.image.get_width(), self.image.get_height()+15), pygame.locals.SRCALPHA)
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
            pygame.gfxdraw.box(new_image, (x, y, w, h), COLOR_OF_HP)
            
            self.image = new_image
            self.rect.height +=7
    
    def update(self):
        self._check_moving()
        self._check_hp()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, color_of_body, color_of_border, pos, degree):
        super().__init__()
        
        self.time_of_birth = pygame.time.get_ticks()
        
        self.max_hp = 1
        self.hp = self.max_hp

        self.speed = pygame.math.Vector2(3, 0).rotate(-degree)
        # 將起始位置從坦克中心移至砲口
        offset = pygame.math.Vector2(self.speed)
        offset.scale_to_length(50)
        self.pos = pos + offset

        self.image = pygame.Surface((30, 30))
        x = self.image.get_width()//2
        y = self.image.get_height()//2
        r = x
        pygame.gfxdraw.filled_circle(self.image, x, y, r, color_of_border)
        border = 3
        r -= border
        pygame.gfxdraw.filled_circle(self.image, x, y, r, color_of_body)

        self.image.set_colorkey(BLACK)
        self.image.set_alpha(0)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=self.pos)
        
        # 紀錄剛碰撞的敵人 避免短時間內不斷檢測
        self.whitelist = pygame.sprite.Group()

    def update(self, *arg):
        self.pos += self.speed
        self.rect.center = self.pos
        
        # 外觀動畫
        alive_time = pygame.time.get_ticks() - self.time_of_birth
        if alive_time<1500 and self.hp>0 and self.image.get_alpha()!=255:
            # 出生時淡入
            alpha = self.image.get_alpha() + 15
            self.image.set_alpha(alpha)
        elif alive_time>1500 or self.hp<=0:
            # 消失時放大
            scale = int(self.image.get_width()*1.06), int(self.image.get_height()*1.06)
            self.image = pygame.transform.scale(self.image, scale)
            self.rect = self.image.get_rect(center=self.pos)
            # 消失時淡出
            alpha = self.image.get_alpha() - 20
            self.image.set_alpha(alpha)
            # 完全淡出後移除
            if self.image.get_alpha() is 0:
                self.kill()

class Tank(pygame.sprite.Sprite):
    def __init__(self, color_of_body, color_of_border):
        super().__init__()

        self.color_of_body = color_of_body
        self.color_of_border = color_of_border
        
        self.acc = 0.03
        self.pos = pygame.math.Vector2(500, 500)
        self.speed = pygame.math.Vector2(0, 0)
        self.max_speed = 1.7
        self.recoil = pygame.math.Vector2(0.000, 0)
        
        self.scale_of_barrel = 1
        
        self.can_attack = True
        self.time_of_attacking = 0
        self.reloading_time = 500

        # 鏡頭移動用
        self.dx = 0
        self.dy = 0

        # 紀錄剛碰撞的敵人 避免短時間內不斷檢測
        self.whitelist = pygame.sprite.Group()

    def update(self, pressed_keys, is_click, mouse_x, mouse_y):
        # 檢查是否有加速度
        if pressed_keys[pygame.locals.K_w]:
            self.speed += (0, -self.acc)
        elif pressed_keys[pygame.locals.K_s]:
            self.speed += (0, self.acc)
        else:
            self.speed.y /= 1.01
            self.speed.y = 0 if abs(self.speed.y) < 0.0000005 else self.speed.y
        if pressed_keys[pygame.locals.K_a]:
            self.speed += (-self.acc, 0)
        elif pressed_keys[pygame.locals.K_d]:
            self.speed += (self.acc, 0)
        else:
            self.speed.x /= 1.01
            self.speed.x = 0 if abs(self.speed.x) < 0.0000005 else self.speed.x

        # 限制速度在指定區間內
        self.speed.x = min(self.max_speed, max(-self.max_speed, self.speed.x))
        self.speed.y = min(self.max_speed, max(-self.max_speed, self.speed.y))
        
        self.pos += self.speed

        # 旋轉角度(https://stackoverflow.com/questions/10473930/how-do-i-find-the-angle-between-2-points-in-pygame)
        # 注意遊戲的座標與常用座標不同(Y軸相反)使用時須加上負號
        dx, dy = mouse_x-self.pos.x, mouse_y-self.pos.y
        degree = degrees(atan2(-dy, dx) % (2*pi))
        
        # 按左鍵發射子彈
        if self.can_attack and is_click:
            self.can_attack = False
            self.time_of_attacking = pygame.time.get_ticks()
            bullet = Bullet(self.color_of_body, self.color_of_border, self.pos, degree)
            player.add(bullet)

        # 若發射後的冷卻期間伸縮砲管
        if not self.can_attack:
            # 從發射後所經過的時間
            elapsed_time = pygame.time.get_ticks() - self.time_of_attacking
            # 前20%的時間收縮
            if elapsed_time < self.reloading_time*0.2:
                self.scale_of_barrel -= 0.003
            # 再20%的時間拉長
            elif elapsed_time < self.reloading_time*0.4:
                self.scale_of_barrel += 0.003
                # 後座力是砲口的反方向
                self.speed += self.recoil.rotate(180-degree)
            # 其餘時間將長度恢復原狀
            elif elapsed_time < self.reloading_time:
                self.scale_of_barrel = 1
            # 冷卻結束
            else:
                self.can_attack = True

        # 因為砲管會收縮所以每次更新都新建重畫
        # 砲管以水平開口朝右繪製 後再根據滑鼠旋轉
        # x,y--------w----------
        # |                    |
        # h                    h
        # |                    |
        # -----------w----------
        self.image = pygame.Surface((100, 100))
        border = 3

        # 畫砲管
        x = self.image.get_width() // 2
        y = self.image.get_height() // 5 * 2
        w = self.image.get_width() // 2 * self.scale_of_barrel
        h = self.image.get_height() // 5
        pygame.gfxdraw.box(self.image, (x,y,w,h), DARK_GRAY)
        x += border
        y += border
        w -= border*2
        h -= border*2
        pygame.gfxdraw.box(self.image, (x,y,w,h), GRAY)
        
        # 畫本體
        x = self.image.get_width() // 2
        y = self.image.get_height() // 2
        r = self.image.get_width() // 4
        pygame.gfxdraw.filled_circle(self.image, x, y, r, self.color_of_border)
        r -= border
        pygame.gfxdraw.filled_circle(self.image, x, y, r, self.color_of_body)
        
        self.image = pygame.transform.rotate(self.image, degree)
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=self.pos)

    
        # # 碰撞檢測
        # for bullet in self.group:
        #     for enemy in pygame.sprite.spritecollide(bullet, enemies, False, pygame.sprite.collide_mask):
        #         can_attack = False if bullet.whitelist.has(enemy) else True
        #         if bullet.hp>0 and enemy.hp>0 and can_attack:
        #             # 互相傷害
        #             bullet.hp -= enemy.damage
        #             enemy.hp -= bullet.damage
        #             bullet.whitelist.add(enemy)

if __name__ == "__main__":
    pygame.init()
    icon = pygame.image.load("icon.png")
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Diepy")
    screen = pygame.display.set_mode((0,0))
    
    # 建立地圖
    world = pygame.Surface((5000, 5000))
    # 填充背景
    world.fill(COLOR_OF_BG)
    # 繪製網格
    world_w, world_h = world.get_size()
    for x in range(0, world_w, 15):
        pygame.gfxdraw.box(world, (x,0,1,world_h), COLOR_OF_GRID)
    for y in range(0, world_h, 15):
        pygame.gfxdraw.box(world, (0,y,world_w,1), COLOR_OF_GRID)
    
    bg = world.copy()

    clock = pygame.time.Clock()

    enemies = pygame.sprite.Group()
    player = pygame.sprite.Group()

    tank = Tank(BLUE, DARK_BLUE)
    player.add(tank)

    is_running = True
    while is_running:

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                is_running = False
        
        # 生成補充的彈藥
        # if len(enemies) < 25:
        #     es = ExpSquare()
        #     enemies.add(es)
        
        # 更新精靈
        pressed_keys = pygame.key.get_pressed()
        is_click = pygame.mouse.get_pressed()[0]
        mouse_x, mouse_y = pygame.mouse.get_pos()
        try:
            # 加上鏡頭位置的偏移
            mouse_x += cam.x
            mouse_y += cam.y
        except:
            # 第一次循環沒有鏡頭偏移
            pass
        player.update(pressed_keys, is_click, mouse_x, mouse_y)
        enemies.update()

        # 更新畫面   
        enemies.clear(world, bg)
        player.clear(world, bg)
        enemies.draw(world)
        player.draw(world)
        
        cam = screen.get_rect()
        cam.center = tank.pos
        cam.x = min(max(cam.x,0),1920) * 0.8
        cam.y = min(max(cam.y,0),1080) * 0.8
        screen.blit(world.subsurface(cam), (0,0))

        pygame.display.update()

        # 設定每秒144幀
        clock.tick(144)

    pygame.quit()
    # sys.exit()