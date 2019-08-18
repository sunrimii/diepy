# import pygame
# import pickle


# rect = pygame.Rect(0,0,1,1)
# print(rect)
# print(pickle.dumps(rect))

a=[1,2,3]
d={"a":a}
print(d.values()[0])
d.values()[0][0] = 0
print(d.values()[0])
