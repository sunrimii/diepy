import pygame
import pickle

pygame.init()
s = pygame.sprite.Sprite()
pickle.dumps(s)

# for event in pygame.event.get():
#             if event.type == pygame.locals.QUIT:
#                 is_running = False


                # for event in pygame.event.get():
                #     if event.type == pygame.QUIT:
                #         running = False
                #     elif event.type == pygame.KEYDOWN:
                #         if event.key == pygame.K_ESCAPE:
                #             running = False