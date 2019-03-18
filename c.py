import socket
import pygame
import pickle





s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1" , 7852))
data = b""
while True:
    packet = s.recv(1024)
    if not packet:
        break
    data += packet



surf = pickle.loads(data)
surf = pygame.surfarray.make_surface(surf)



pygame.init()
screen = pygame.display.set_mode()



running = True
while running:
    screen.blit(surf, (0,0))
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False