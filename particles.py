import pygame
import random

class Particle:
    def __init__(self, x, y, style="spark"):
        self.x, self.y = x, y; self.style = style
        if style=="spark":
            self.vx=random.uniform(-4,4); self.vy=random.uniform(-6,-1)
            self.life=255; self.r=random.randint(200,255); self.g=random.randint(140,200)
        elif style=="mist":
            self.vx=random.uniform(-0.5,0.5); self.vy=random.uniform(-0.3,-0.1)
            self.life=random.randint(80,160); self.r=30; self.g=50
        elif style=="blood":
            self.vx=random.uniform(-3,3); self.vy=random.uniform(-4,2)
            self.life=255; self.r=180; self.g=0

    def update(self):
        self.x+=self.vx; self.y+=self.vy
        decay=8 if self.style=="spark" else (3 if self.style=="mist" else 10)
        self.life-=decay
        if self.style=="spark": self.vy+=0.2
        return self.life>0

    def draw(self, surf):
        a=max(0,min(255,self.life))
        if self.style=="mist":
            s=pygame.Surface((20,10),pygame.SRCALPHA); s.fill((self.r,self.g,20,a//2))
            surf.blit(s,(int(self.x)-10,int(self.y)-5))
        elif self.style=="blood":
            pygame.draw.circle(surf,(self.r,0,0),(int(self.x),int(self.y)),max(1,int(a/80)))
        else:
            pygame.draw.circle(surf,(self.r,self.g,0),(int(self.x),int(self.y)),max(1,int(a/80)))
