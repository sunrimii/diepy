import socket
import pygame
import pickle


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1" , 7852))
s.listen(5)
conn, addr = s.accept()
print(conn, addr)

surf = pygame.Surface((100,100))
surf.fill((0,255,0))
string = pygame.image.tostring(surf, "RGB")
data = pickle.dumps(string)

conn.sendall(data)
conn.close()
s.close()

