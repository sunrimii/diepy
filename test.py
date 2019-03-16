import pygame
import socket

pygame.init()
surf = pygame.Surface((10,10))
pygame.surfarray.array2d(surf)

# for event in pygame.event.get():
#             if event.type == pygame.locals.QUIT:
#                 is_running = False


                # for event in pygame.event.get():
                #     if event.type == pygame.QUIT:
                #         running = False
                #     elif event.type == pygame.KEYDOWN:
                #         if event.key == pygame.K_ESCAPE:
                #             running = False