import pygame
import random
from config import CELL_SIZE

def make_background():
    """Create the background surface with texture"""
    surf = pygame.Surface((900, 900))
    surf.fill((18, 30, 15))
    rng = random.Random(42)
    for _ in range(600):
        x, y = rng.randint(0, 900), rng.randint(0, 900)
        r = rng.randint(2, 12); g = rng.randint(22, 45); b = rng.randint(10, 22)
        pygame.draw.ellipse(surf, (r, g, b), (x-4, y-2, 8, 4))
    edge = pygame.Surface((900, 900), pygame.SRCALPHA)
    for i in range(80):
        alpha = int(i * 1.8)
        pygame.draw.rect(edge, (0, 0, 0, alpha), (i, i, 900-2*i, 900-2*i), 1)
    surf.blit(edge, (0, 0))
    return surf

def make_zombie_sprite():
    """Create a pixelated zombie sprite"""
    W, H = 22, 28
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    def px(x, y, color): surf.set_at((x, y), color)
    def rect(x, y, w, h, color):
        for dy in range(h):
            for dx in range(w): surf.set_at((x+dx, y+dy), color)
    skin=(130,180,120); coat=(90,55,20); shirt=(200,50,50)
    pants=(50,80,140); eyes_c=(230,230,180); hair_c=(60,80,50); mouth=(160,60,50)
    rect(7,1,8,7,skin); px(8,0,hair_c); px(9,0,hair_c); px(11,0,hair_c)
    rect(8,3,2,2,eyes_c); rect(12,3,2,2,eyes_c)
    px(9,4,(20,20,20)); px(13,4,(20,20,20))
    rect(9,7,4,1,mouth); rect(10,8,2,1,skin)
    rect(5,9,12,8,coat); rect(9,10,4,6,shirt)
    rect(5,9,3,5,coat); rect(14,9,3,5,coat)
    rect(3,9,2,7,skin); rect(17,9,2,6,coat)
    rect(2,15,3,2,skin); rect(17,14,3,2,skin)
    rect(7,17,4,8,pants); rect(11,17,4,8,pants)
    rect(6,25,5,3,(30,20,10)); rect(11,25,5,3,(30,20,10))
    return surf

def make_task_sprite():
    """Create a task/completion marker sprite"""
    s = pygame.Surface((24, 24), pygame.SRCALPHA)
    pygame.draw.polygon(s, (90,90,90), [(12,2),(22,20),(2,20)])
    pygame.draw.polygon(s, (60,60,60), [(12,2),(22,20),(2,20)], 1)
    pygame.draw.line(s, (0,220,180), (12,6), (12,17), 2)
    pygame.draw.line(s, (0,220,180), (7,11), (17,11), 2)
    return s

def make_lamp_sprite():
    """Create a lamp/light post sprite"""
    s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    cx, cy = CELL_SIZE//2, CELL_SIZE//2
    pygame.draw.rect(s, (80,60,30), (cx-1, cy-2, 3, cy+2))
    pygame.draw.circle(s, (60,50,20), (cx, cy-4), 5)
    pygame.draw.circle(s, (255,220,100), (cx, cy-4), 3)
    return s

# Global sprite instances
ZOMBIE_SPRITE = make_zombie_sprite()
TASK_SPRITE = make_task_sprite()
LAMP_SPRITE = make_lamp_sprite()
