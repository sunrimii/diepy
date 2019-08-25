import pygame

v1 = pygame.math.Vector2(1, 0)
v1.rotate_ip(88)

v2 = pygame.math.Vector2(1, 0)
print(v1.angle_to(v2))