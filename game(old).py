from math import atan2, degrees, pi, sin, cos
from random import randrange

import pygame
import pygame.gfxdraw
import pygame.freetype
import pygame.locals


# 顏色定義
COLOR_OF_BG = (220, 220, 220)
COLOR_OF_GRID = (215, 215, 215)
COLOR_OF_SLOWZONE = (210, 210, 210)
COLOR_OF_HP = (100, 200, 100)
BLACK = (0, 0, 0)
WHITE = (250, 250, 250)
BLUE = (20, 180, 223)
DARK_BLUE = (20, 143, 175)
DARK_GRAY = (123, 123, 123)
YELLOW = (255, 232, 106)
DARK_YELLOW = (190, 176, 78)
GRAY = (157, 157, 157)


class Trigon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.time_of_birth = pygame.time.get_ticks()

        self.max_hp = 1
        self.hp = self.max_hp

        self.image_orig = pygame.Surface((30, 30))
        # x2,y2
        #      x1,y1
        # x3,y3
        x1 = self.image_orig.get_width()
        y1 = self.image_orig.get_height() // 2
        x2 = 0
        y2 = 0
        x3 = 0
        y3 = self.image_orig.get_height()
        pygame.gfxdraw.filled_trigon(self.image_orig, x1, y1, x2, y2, x3, y3, DARK_GRAY)
        border = 3
        x1 -= border*5//2
        x2 += border
        y2 += border*2
        x3 += border
        y3 -= border*2
        pygame.gfxdraw.filled_trigon(self.image_orig, x1, y1, x2, y2, x3, y3, GRAY)

        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.image_scale = self.image_orig.get_size()
        self.image_alpha = 0
        
        # 隨機起始位置
        x, y = randrange(game.world_w), randrange(game.world_h)
        self.pos = pygame.math.Vector2(x, y)
        self.rect = self.image.get_rect(center=self.pos)
    
    def update(self):
        # distance_to(Vector2) -> float
        # 追蹤最接近的坦克
        dx, dy = game.tank.pos.x-self.pos.x, game.tank.pos.y-self.pos.y
        degs = degrees(atan2(-dy, dx))
        
        self.image = pygame.transform.rotate(self.image_orig, degs)
        
        self.mask = pygame.mask.from_surface(self.image)

        # 更新位置
        self.speed = pygame.math.Vector2(0.8, 0).rotate(-degs)
        self.pos += self.speed
        self.rect = self.image.get_rect(center=self.pos)

        # 外觀動畫
        alive_time = pygame.time.get_ticks() - self.time_of_birth
        if alive_time<1500 and (self.hp>0) and self.image_alpha!=255:
            # 出生時淡入
            self.image_alpha += 15
            self.image.set_alpha(self.image_alpha)
        elif self.hp == 0:
            # 消失時放大
            self.image_scale = int(self.image_scale[0]*1.055), int(self.image_scale[1]*1.06)
            self.image = pygame.transform.scale(self.image, self.image_scale)
            self.rect.size = self.image.get_size()
            # 消失時淡出
            self.image_alpha -= 10
            self.image.set_alpha(self.image_alpha)
            # 完全淡出後移除
            if self.image_alpha <= 0:
                self.kill()
        
        # 受傷時顯示血量
        elif 0 < self.hp < self.max_hp:
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

class Bullet(pygame.sprite.Sprite):
    def __init__(self, color_of_body, color_of_border, pos, degs):
        super().__init__()
        
        self.time_of_birth = pygame.time.get_ticks()
        
        self.is_alive = True

        self.speed = pygame.math.Vector2(3.5, 0).rotate(-degs)
        
        # 將起始位置從坦克中心移至砲口
        offset = pygame.math.Vector2(self.speed)
        offset.scale_to_length(50)
        self.pos = pos + offset

        self.image = pygame.Surface((30, 30))
        x = self.image.get_width() // 2 - 1
        y = self.image.get_height() // 2
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
        if alive_time<1500 and self.is_alive and self.image.get_alpha()!=255:
            # 出生時淡入
            alpha = self.image.get_alpha() + 15
            self.image.set_alpha(alpha)
        elif (not self.is_alive) or alive_time>1500:
            # 消失時放大
            scale = int(self.image.get_width()*1.06), int(self.image.get_height()*1.06)
            self.image = pygame.transform.scale(self.image, scale)
            self.rect.size = self.image.get_size()
            # 消失時淡出
            alpha = self.image.get_alpha() - 20
            self.image.set_alpha(alpha)
            # 完全淡出後移除
            if self.image.get_alpha() is 0:
                self.kill()

        # 碰撞檢測
        if self.is_alive:
            for enemy in pygame.sprite.spritecollide(self, game.enemies, False, pygame.sprite.collide_mask):
                if enemy.hp > 0:
                    self.is_alive = False
                    enemy.hp -= 1
                    #do something

class BulletPack(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.is_alive = True

        # 抽五次後選擇最小的可以降低抽到大數的機率
        self.num_of_bullets = min([randrange(100, 500) for _ in range(5)])
        
        # 隨機起始位置
        x, y = randrange(game.world_w), randrange(game.world_h)
        self.pos = pygame.math.Vector2(x, y)

        self.speed = pygame.math.Vector2(0.05, 0)
        degs = randrange(360)
        self.speed = self.speed.rotate(degs)

        # 外觀大小由持有數量所決定(由一區間映射至另一區間)
        x = y = r = int( (self.num_of_bullets-100)*(40-15)/(500-100) + 15 )
        self.image = pygame.Surface((r*2, r*2))
        pygame.gfxdraw.filled_circle(self.image, x, y, r, DARK_YELLOW)
        border = 3
        r -= border
        pygame.gfxdraw.filled_circle(self.image, x, y, r, YELLOW)

        self.image.set_colorkey(BLACK)
        self.image.set_alpha(0)

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()

    def update(self):
        self.pos += self.speed
        self.rect.center = self.pos
        
        # 外觀動畫
        if self.is_alive and self.image.get_alpha()!=255:
            # 出生時淡入
            alpha = self.image.get_alpha() + 15
            self.image.set_alpha(alpha)
        elif not self.is_alive:
            # 消失時放大
            scale = int(self.image.get_width()*1.06), int(self.image.get_height()*1.06)
            self.image = pygame.transform.scale(self.image, scale)
            self.rect.size = self.image.get_size()
            # 消失時淡出
            alpha = self.image.get_alpha() - 20
            self.image.set_alpha(alpha)
            # 完全淡出後移除
            if self.image.get_alpha() is 0:
                self.kill()

class Tank(pygame.sprite.Sprite):
    def __init__(self, color_of_body, color_of_border):
        super().__init__()

        self.is_alive = True

        self.color_of_body = color_of_body
        self.color_of_border = color_of_border
        
        self.acc = 0.025
        self.pos = pygame.math.Vector2(500, 500)
        self.speed = pygame.math.Vector2(0, 0)
        self.max_speed = 2.3
        self.recoil = pygame.math.Vector2(0, 0)
        
        self.scale_of_barrel = 1
        
        self.num_of_bullets = 1
        self.is_reloading = False
        self.time_of_attacking = 0
        self.reloading_time = 200

    def update(self, pressed_keys, is_click, mouse_x, mouse_y):
        # 檢查是否有加速度
        if pressed_keys[pygame.locals.K_w]:
            self.speed += (0, -self.acc)
        elif pressed_keys[pygame.locals.K_s]:
            self.speed += (0, self.acc)
        else:
            self.speed.y /= 1.005
            self.speed.y = 0 if abs(self.speed.y) < 0.00000005 else self.speed.y
        
        if pressed_keys[pygame.locals.K_a]:
            self.speed += (-self.acc, 0)
        elif pressed_keys[pygame.locals.K_d]:
            self.speed += (self.acc, 0)
        else:
            self.speed.x /= 1.005
            self.speed.x = 0 if abs(self.speed.x) < 0.00000005 else self.speed.x

        # 限制移動速度
        self.speed.x = min(self.max_speed, max(-self.max_speed, self.speed.x))
        self.speed.y = min(self.max_speed, max(-self.max_speed, self.speed.y))
        
        self.pos += self.speed

        # 若進入地圖邊緣會減速
        in_slow_zone = (not(300<self.pos.x<game.world_w-300)) or (not(300<self.pos.y<game.world_h-300))
        if in_slow_zone:
            self.speed /= 1.05

        # 限制移動邊界
        self.pos.x = min(max(self.pos.x, 0), game.world_w)
        self.pos.y = min(max(self.pos.y, 0), game.world_h)

        # 旋轉角度(https://stackoverflow.com/questions/10473930/how-do-i-find-the-angle-between-2-points-in-pygame)
        # 注意遊戲的座標與常用座標不同(Y軸相反)使用時須加上負號
        dx, dy = mouse_x-self.pos.x, mouse_y-self.pos.y
        degs = degrees(atan2(-dy, dx))
        
        # 按左鍵發射子彈
        if (not self.is_reloading) and is_click and (self.num_of_bullets>0):
            self.is_reloading = True
            self.time_of_attacking = pygame.time.get_ticks()
            bullet = Bullet(self.color_of_body, self.color_of_border, self.pos, degs)
            game.player.add(bullet)
            self.num_of_bullets -= 1

        # 若發射後的冷卻期間伸縮砲管
        if self.is_reloading:
            # 從發射後所經過的時間
            elapsed_time = pygame.time.get_ticks() - self.time_of_attacking
            # 前20%的時間收縮
            if elapsed_time < self.reloading_time*0.2:
                self.scale_of_barrel -= 0.003
            # 再20%的時間拉長
            elif elapsed_time < self.reloading_time*0.4:
                self.scale_of_barrel += 0.003
                # 後座力是砲口的反方向
                self.speed += self.recoil.rotate(180-degs)
            # 其餘時間將長度恢復原狀
            elif elapsed_time < self.reloading_time:
                self.scale_of_barrel = 1
            # 冷卻結束
            else:
                self.is_reloading = False

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
        
        self.image = pygame.transform.rotate(self.image, degs)
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=self.pos)

        # 碰撞檢測
        if self.is_alive:
            for enemy in pygame.sprite.spritecollide(self, game.enemies, False, pygame.sprite.collide_mask):
                if enemy.hp > 0:
                    pass
                    # self.is_alive = False
            for bullet_pack in pygame.sprite.spritecollide(self, game.bullet_packs, False, pygame.sprite.collide_mask):
                if bullet_pack.is_alive:
                    self.num_of_bullets += bullet_pack.num_of_bullets
                    bullet_pack.is_alive = False

class Game:
    def __init__(self):
        # 基本設定
        pygame.init()
        pygame.display.set_caption("Diepy")
        icon = pygame.image.load("icon.png")
        pygame.display.set_icon(icon)
        self.screen = pygame.display.set_mode()
        
        # 建立地圖
        self.world = pygame.Surface((5000, 5000))
        self.world.fill(COLOR_OF_BG)
        # 繪製減速區
        self.world_w, self.world_h = self.world.get_size()
        pygame.gfxdraw.box(self.world, (0,0,self.world_w,300), COLOR_OF_SLOWZONE)
        pygame.gfxdraw.box(self.world, (0,0,300,self.world_h), COLOR_OF_SLOWZONE)
        pygame.gfxdraw.box(self.world, (0,self.world_h-300,self.world_w,300), COLOR_OF_SLOWZONE)
        pygame.gfxdraw.box(self.world, (self.world_w-300,0,300,self.world_h), COLOR_OF_SLOWZONE)
        # 繪製網格
        for x in range(0, self.world_w, 20):
            pygame.gfxdraw.box(self.world, (x,0,2,self.world_h), COLOR_OF_GRID)
        for y in range(0, self.world_h, 20):
            pygame.gfxdraw.box(self.world, (0,y,self.world_w,2), COLOR_OF_GRID)

        self.bg = self.world.copy()

        self.clock = pygame.time.Clock()

        self.enemies = pygame.sprite.Group()
        self.bullet_packs = pygame.sprite.Group()
        self.player = pygame.sprite.Group()

        self.tank = Tank(BLUE, DARK_BLUE)
        self.player.add(self.tank)
        
        self.cam = pygame.Rect(0, 0, 1920, 1080)
        self.cam.center = self.tank.pos

        self.is_running = True

    def handle_events(self):
        self.pressed_keys = pygame.key.get_pressed()
        self.is_click = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()
        self.mouse_x, self.mouse_y = mouse_pos
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
    
    def run_logic(self):
        # 生成補充的彈藥
        if len(self.bullet_packs) < 20:
            bp = BulletPack()
            self.bullet_packs.add(bp)
        
        # 生成敵人
        if len(self.enemies) < 30:
            trigon = Trigon()
            self.enemies.add(trigon)
        
        # 更新精靈
        try:
            # 加上鏡頭位置的偏移
            self.mouse_x += self.cam.x
            self.mouse_y += self.cam.y
        except:
            # 第一次循環沒有鏡頭偏移
            pass
        self.player.update(self.pressed_keys, self.is_click, self.mouse_x, self.mouse_y)
        self.enemies.update()
        self.bullet_packs.update()

        # 更新畫面
        self.enemies.clear(self.world, self.bg)
        self.bullet_packs.clear(self.world, self.bg)
        self.player.clear(self.world, self.bg)
        self.enemies.draw(self.world)
        self.bullet_packs.draw(self.world)
        self.player.draw(self.world)

        # 使鏡頭平滑移動
        self.cam.center += (self.tank.pos-self.cam.center) * 0.1

        # 限制移動邊界
        self.cam.x = min(max(self.cam.x, 0), self.world_w-self.cam.w) 
        self.cam.y = min(max(self.cam.y, 0), self.world_h-self.cam.h)

        # 將鏡頭內的畫面顯示於螢幕上
        self.screen.blit(self.world.subsurface(self.cam), (0,0))
        
        # 於右下角顯示剩餘子彈數
        text = "x" + str(self.tank.num_of_bullets)
        font = pygame.font.SysFont("impact", 40)
        font_surf = font.render(text, True, BLACK)
        x = 1700
        y = 500
        self.screen.blit(font_surf, (x,y))
        font_surf = font.render(text, True, WHITE)
        x -= 3
        y -= 3
        self.screen.blit(font_surf, (x,y))

    def update_screen(self):
        self.clock.tick(144)
        pygame.display.update()


if __name__ == "__main__":
    game = Game()

    while game.is_running:
        game.handle_events()
        game.run_logic()
        game.update_screen()
    
    pygame.quit()