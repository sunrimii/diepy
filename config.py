BG_COLOR = (210, 210, 210)
HP_COLOR = (100, 200, 100)
BLACK = (0, 0, 0)
DARK_BLUE = (20, 143, 175)
BLUE = (20, 180, 223)
DARK_GRAY = (123, 123, 123)
GRAY = (157, 157, 157)
YELLOW = (255, 232, 106)
DARK_YELLOW = (190, 176, 78)

TANK_MAX_HP = 10
TANK_HP_REGEN = 0.5
TANK_DAMAGE = 3
TANK_ACC = 0.02
TANK_RELOADING_TIME = 500
TANK_INIT_POS = (500, 500)
TANK_MAX_SPEED = 1.7
TANK_RECOIL = 0.01

"""
子彈 若有重複則按比率
    橢圓形 爆炸
    三角形 穿透
    正方形 緩速
    十字形 治療
    隕石型 燃燒

砲管
    增加長度 射程
    加粗寬度 大小
    兩段砲管 後座
    閃電標誌 冷卻
    增加個數 

本體
    



子彈增加血量 加粗外框 
子彈增加治療 子彈畫十字
子彈能緩速 外觀變方形



pygame.gfxdraw.filled_circle(self.image, 15, 15, 12, BLUE)
"""