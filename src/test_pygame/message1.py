import sys
import pygame
from pygame.locals import *

white = 255,255,255
blue  = 0,0,200

pygame.init()
#screen = pygame.display.set_mode((600,500))
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.NOFRAME)

pygame.font.init()
myfont = pygame.font.Font(None,60)
textImage = myfont.render("Hello Pygame", True, white)
screen.fill(blue)
screen.blit(textImage, (100,100))
pygame.display.update()

while (True):
    event = pygame.event.wait()
    if event.type == QUIT:
        pygame.quit()
        sys.exit()
