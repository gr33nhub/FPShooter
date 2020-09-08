
import pygame
import random
import math
import logging

from pygame.locals import K_ESCAPE, K_SPACE, KEYDOWN, QUIT

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

WAIT_AFTER_HIT_DURATION = 250
WAIT_BEFORE_START_DURATION = 255
SHRINKING_SPEED = 180 # More is faster

TARGET_RADIUS = 400
HIT_RADIUS = 8

HIT_DURATION = 85



class Player():
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.target = Target()
        
    def add_to_score(self, points):
        self.score += points
        

    def update(self):
        self.score += self.target.update()

        name_text = font.render("{}".format(self.name), True, BLACK, WHITE)
        screen.blit(name_text, [10, 10])
       
        score_text = font.render("Punkte: {}".format(self.score), True, BLACK, WHITE)
        screen.blit(score_text, [10, SIZE[1]-20])


    def create_bullet_hole(self, x, y):
        self.score += self.target.create_bullet_hole(x, y)


        
    
    

class Target():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.counter = 0
        self.new_target()


    def new_target(self):
        self.x = random.randint(int(SIZE[0]*0.1), int(SIZE[0]*0.9))
        self.y = random.randint(int(SIZE[1]*0.1), int(SIZE[1]*0.9))
        self.target_new = True
        self.radius = TARGET_RADIUS
        self.wait_after_hit = False
        self.wait_after_hit_duration = WAIT_AFTER_HIT_DURATION
        self.target_new_time = WAIT_BEFORE_START_DURATION
        self.color = RED


    def update(self):
        if self.target_new: # neues Ziel, etwas warten
            if self.target_new_time > 0:
                self.target_new_time -= 1
                self.color = (self.target_new_time, 0, 0) #change color from red to black
            else:
                self.target_new = False
                self.color = BLACK
        else:                
            if self.wait_after_hit: # stop after hit / new target after time
                if self.wait_after_hit_duration > 0:
                    self.wait_after_hit_duration -= 1
                else:
                    self.counter += 1
                    self.new_target()
            else:
                if self.radius > 8: 
                    self.radius -= (self.radius / SHRINKING_SPEED)
                else: # target too small
                    self.counter += 1
                    self.new_target()
                    return HARD_PUNISH

                
        # draw target first
        pygame.draw.circle(screen, self.color, (self.x,self.y), int(self.radius), 0)
        
        current_radius = font.render("Radius: {:.0f}".format(self.radius), True, BLACK, WHITE)
        screen.blit(current_radius, [10, SIZE[1]-45])
        
        return 0


    def create_bullet_hole(self, x, y):
        if self.target_new: # hit before start
            hits.append(Bullet_Hole(x, y, RED, HARD_PUNISH))
            return HARD_PUNISH
        elif self.wait_after_hit: # nach einem Treffer
            hits.append(Bullet_Hole(x, y, RED, HARD_PUNISH))
            return HARD_PUNISH
        else:
            # calculate if hit  
            if math.sqrt((self.x - x)**2 + ( self.y - y)**2) <= self.radius:
                hits.append(Bullet_Hole(x, y, GREEN, int(self.radius)))
                self.wait_after_hit = True
                return int(self.radius)
            else: # Miss
                hits.append(Bullet_Hole(x, y, RED, SOFT_PUNISH))
                return SOFT_PUNISH
        return 0
            


class Bullet_Hole():
    def __init__(self, x, y, color, score):
        self.x = x
        self.y = y
        self.radius = HIT_RADIUS
        self.duration =  HIT_DURATION
        self.color = color
        self.score = score
        self.score_position = 0

    def update(self):
        if self.duration < HIT_RADIUS:
            self.radius = self.duration 
        pygame.draw.circle(screen, self.color, (self.x,self.y), int(self.radius), 0)
        score_text = font.render("{}".format(self.score), True, self.color)
        screen.blit(score_text, [self.x + 10, self.y - 10 + int(self.score_position)])
        self.duration -= 1
        self.score_position -= 0.5


hits=[]
players = []
#all_sprite_list = pygame.sprite.Group()
#bullet_hole_list = pygame.sprite.Group()

players.append(Player("a"))
players.append(Player("b"))
players.append(Player("c"))
        
def main():
    pygame.init()
    pygame.display.set_caption("FPShooter")
    clock = pygame.time.Clock()
    
    current_player = 0

    running = True
    display_instructions = True
    gameover = False
    
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

        clock.tick(20)
        pygame.display.flip()

        
    while running and not gameover:

        screen.fill( WHITE )
        pygame.draw.line(screen, GRAY, (int(SIZE[0]/2), 0), (int(SIZE[0]/2), int(SIZE[1])))
        pygame.draw.line(screen, GRAY, (0, int(SIZE[1]/2)), (int(SIZE[0]), int(SIZE[1]/2)))

        if players[current_player].target.counter >= 2:
            current_player += 1
            if current_player >= len(players):
                running = False
        else:
            players[current_player].update()

        # then draw all hits
        for hit in hits:
            if hit.duration > 0:
                hit.update()
            else:
                hits.remove(hit)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_SPACE:
                    x = random.randint(SIZE[0]*0.2, SIZE[0]*0.8)
                    y = random.randint(SIZE[0]*0.2, SIZE[0]*0.8)
                    players[current_player].create_bullet_hole(x, y)


        clock.tick(100)
        pygame.display.flip()


        
    while not gameover and False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameover = True
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    gameover = True
                    
        screen.fill( GRAY )

        offset = 0
        
        for player in players:
            score_text = font.render("{}: {}".format(player.name, player.score), True, BLACK)
            screen.blit(score_text, [10, 10 + offset])
            offset += 25

        clock.tick(20)
        pygame.display.flip()
        

    pygame.quit()


if __name__ == "__main__":
    main()