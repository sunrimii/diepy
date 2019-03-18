import socket
import pygame
import pickle


# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind(("127.0.0.1" , 7852))
# s.listen(5)
# conn, addr = s.accept()
# print (conn, addr)





surf = pygame.Surface((100,100))
surf.fill((0,255,0))

a = surf.copy()
a.fill((255,255,0))

surf = pygame.surfarray.array2d(surf)
print(surf)

a = pygame.surfarray.array2d(a)
print(a)

b = pygame.surfarray.make_surface(a)
b = pygame.surfarray.array2d(b)
print(b)
# data = pickle.dumps(surf)

# surf = pickle.loads(data)
# surf = pygame.surfarray.make_surface(surf)


# for i in range(len(AAA)):
#     if surf[i] != AAA[i]:
#         print("123")



# pygame.init()
# screen = pygame.display.set_mode()



# running = True
# while running:
#     screen.blit(surf, (0,0))
#     pygame.display.update()
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         elif event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_ESCAPE:
#                 running = False



# conn.send(data)
# conn.close()
# s.close()

