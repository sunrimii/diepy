import pygame
screen = pygame.display.set_mode((640,480))
img = pygame.image.load("image.webp")

for opacity in range(255, 0, -15):
     work_img = img.copy()
     pygame.draw.rect(work_img, (255,0, 0, opacity),  (0,0, 640,480))
     screen.blit(work_img, (0,0))
     pygame.display.flip()
     pygame.time.delay(100)