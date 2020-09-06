
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
GRAY = ( 100, 100, 100)
WHITE = ( 255, 255, 255)
GREEN = ( 0, 255, 0)
BLUE= (0,191,255)
RED = ( 255, 0, 0)

SIZE = (500, 500)

pygame.font.init()

font = pygame.font.Font(None, 36)

screen = pygame.display.set_mode(SIZE)

HARD_PUNISH = 500 #1000
SOFT_PUNISH = 250




class Target():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.score = 0
        self.radius = 400
        self.speed = 180
        self.stop_duration = 250
        self.stop = False
        self.hits = []
        self.new_target()
        

    def new_target(self):
        self.x = random.randint(int(SIZE[0]*0.1), int(SIZE[0]*0.9))
        self.y = random.randint(int(SIZE[1]*0.1), int(SIZE[1]*0.9))
        logging.debug(self.x, self.y)
        self.radius = 400
        self.target_new = True
        self.target_new_time = 255
        self.color = RED
        

    def update(self):
        if self.target_new: # neues Ziel, etwas warten
            self.target_new_time -= 1
            self.color = (self.target_new_time, 0, 0) #change color from red to black
            if self.target_new_time <= 1:
                self.target_new = False
                self.color = BLACK
        else:                
            if self.stop: # stop after hit / new target after time
                self.stop_duration -= 1
                if self.stop_duration <= 1:
                    self.stop = False
                    self.stop_duration = 150
                    self.new_target()

            else:
                self.radius -= self.radius / self.speed
                if self.radius < 8:
                    self.score += HARD_PUNISH
                    self.new_target()

                
        # draw target first
        pygame.draw.circle(screen, self.color, (self.x,self.y), int(self.radius), 0)

        # then draw all hits
        for hit in self.hits:
            if hit.duration <= 1:
                self.hits.remove(hit)
            else:
                hit.update()

        score_text = font.render("Punkte: {}".format(self.score), True, BLACK, WHITE)
        current_radius = font.render("Radius: {:.0f}".format(self.radius), True, BLACK, WHITE)
        screen.blit(score_text, [10, SIZE[1]-20])
        screen.blit(current_radius, [10, SIZE[1]-45])
        

    def create_bullet_hole(self, x, y):
        if self.target_new: # hit before start
            self.score += HARD_PUNISH
            self.hits.append(Bullet_Hole(x, y, RED))
        elif self.stop: # nach einem Treffer
            self.score += HARD_PUNISH
            self.hits.append(Bullet_Hole(x, y, RED))
        else:
            # calculate if hit  
            if math.sqrt((self.x - x)**2 + ( self.y - y)**2) <= self.radius:
                self.score += int(self.radius)
                logging.info("treffer {}".format(self.radius))
                logging.info("self.x {}, self.y {}, x {}, y {}".format(self.x, self.y, x, y))
                self.hits.append(Bullet_Hole(x, y, GREEN))
                self.stop=True
            else: # Miss
                self.score += SOFT_PUNISH
                self.hits.append(Bullet_Hole(x, y, RED))
            


class Bullet_Hole():
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.duration = 50
        self.color = color

    def update(self):
        self.duration -= 1
        hit_radius = self.duration / 2
        pygame.draw.circle(screen, self.color, (self.x,self.y), int(hit_radius), 0)





        
def main():

    pygame.init()

    pygame.display.set_caption("FPShooter")
    clock = pygame.time.Clock()
    
    target = Target()


    running = True
    display_instructions = True
    
    while running and display_instructions and False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_SPACE:
                    display_instructions = False
                    
        instruction_text = font.render("Instructions", True, WHITE)
        screen.blit(instruction_text, [10, 10])


            # Limit to 60 frames per second
        clock.tick(20)
     
        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        
    while running:

        screen.fill( WHITE )
        pygame.draw.line(screen, GRAY, (int(SIZE[0]/2), 0), (int(SIZE[0]/2), int(SIZE[1])))
        pygame.draw.line(screen, GRAY, (0, int(SIZE[1]/2)), (int(SIZE[0]), int(SIZE[1]/2)))

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
