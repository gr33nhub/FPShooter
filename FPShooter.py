
import pygame
import random
import math
import logging

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    QUIT,
)

BLACK = ( 0, 0, 0)
WHITE = ( 255, 255, 255)
GREEN = ( 0, 255, 0)
BLUE= (0,191,255)
RED = ( 255, 0, 0)



SIZE = (500, 500)




class Target():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.radius = 400
        self.speed = 180
        self.stop_duration = 250
        self.stop = False
        self.hits = []
        self.new_target()
        

    def new_target(self):
        self.x = random.randint(SIZE[0]*0.1, SIZE[0]*0.9)
        self.y = random.randint(SIZE[1]*0.1, SIZE[1]*0.9)
        logging.debug(self.x, self.y)
        self.radius = 400
        

    def update(self):
        if not self.stop:
            
            self.radius = self.radius - (self.radius / self.speed )
            if self.radius < 8:
                self.new_target()
        else:
            self.stop_duration -= 1
            if self.stop_duration <= 1:
                self.stop = False
                self.stop_duration = 150
                self.new_target()
                
        pygame.draw.circle(screen, BLACK, (self.x,self.y), int(self.radius), 0)

        for hit in self.hits:
            if hit.duration <= 1:
                self.hits.remove(hit)
            else:
                hit.update()


    def create_bullet_hole(self, x, y):
        if math.sqrt((self.x - x)**2 + ( self.y - y)**2) <= self.radius:
            logging.info("treffer {}".format(self.radius))
            logging.info("self.x {}, self.y {}, x {}, y {}".format(self.x, self.y, x, y))
            self.hits.append(Bullet_Hole(x, y, True))

  
            self.stop=True
        else:
            self.hits.append(Bullet_Hole(x, y, False))
            


class Bullet_Hole():
    def __init__(self, x, y, Hit=False):
        self.x = x
        self.y = y
        self.duration = 50
        self.hit = Hit

    def update(self):
        self.duration -= 1
        hit_radius = self.duration / 2
        if self.hit:
            pygame.draw.circle(screen, GREEN, (self.x,self.y), int(hit_radius), 0)
        else:
            pygame.draw.circle(screen, RED, (self.x,self.y), int(hit_radius), 0)




screen = pygame.display.set_mode(SIZE)
        
def main():

    pygame.init()

    pygame.display.set_caption("FPShooter")
    clock = pygame.time.Clock()
    
    target = Target()


    running = True
    while running:
        
        screen.fill( WHITE )
        target.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_SPACE:
                    x = random.randint(SIZE[0]*0.2, SIZE[0]*0.8)
                    y = random.randint(SIZE[0]*0.2, SIZE[0]*0.8)
                    target.create_bullet_hole(x, y)

        
        clock.tick(100)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
