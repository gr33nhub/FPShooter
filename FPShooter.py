import pygame
import random
import math
from enum import Enum

from pygame.locals import K_ESCAPE, K_BACKSPACE, K_SPACE, K_RETURN, KEYDOWN, QUIT

################################################################################
PlayerNames=["Gonny", "Python", "Hans"]
NumberTargets = 2 #Targets per player
################################################################################

BLACK = ( 0, 0, 0)
GRAY = ( 100, 100, 100)
WHITE = ( 255, 255, 255)
GREEN = ( 0, 255, 0)
BLUE= (0,191,255)
RED = ( 255, 0, 0)

SIZE = (500, 500)



HARD_PUNISH = 500 #1000
SOFT_PUNISH = 250

WAIT_AFTER_HIT_DURATION = 250
WAIT_BEFORE_START_DURATION = 255
SHRINKING_SPEED = 180 # More is faster

TARGET_RADIUS = 400.0
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


        
    
class State(Enum):
    NEW = 1
    BEFORE_SHRINK = 2
    SHRINK = 3
    AFTER =4
    HIT = 5
    MISS = 6




WAIT_BEFORE_SHRINK = 255
WAIT_AFTER = 200



class Target():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.counter = 0
        self.hits = []
        self.new_target()



    def new_target(self):
        self.x = random.randint(int(SIZE[0]*0.1), int(SIZE[0]*0.9))
        self.y = random.randint(int(SIZE[1]*0.1), int(SIZE[1]*0.9))
        self.state = State.NEW
        self.timer = WAIT_BEFORE_SHRINK     

        self.radius = TARGET_RADIUS
        self.color = RED


    def update(self):

        pygame.draw.circle(screen, self.color, (self.x,self.y), int(self.radius), 0)
        
        current_radius = font.render("Radius: {:.0f}".format(self.radius), True, BLACK, WHITE)
        screen.blit(current_radius, [10, SIZE[1]-45])

        returnvalue = 0

        #print("{}".format(self.state), end='\r', flush=True)
        
        if self.state == State.NEW:
            self.state = State.BEFORE_SHRINK
            self.timer = WAIT_BEFORE_SHRINK 
        
        elif self.state == State.BEFORE_SHRINK:
            if self.timer > 0:
                self.timer -= 1
                if self.timer > 254:
                    self.color = RED
                else:
                    self.color = (self.timer, 0, 0)
            else:
                self.state = State.SHRINK
                self.color = BLACK
        
        elif self.state == State.SHRINK:
            if self.radius > 8: 
                    self.radius -= (self.radius / SHRINKING_SPEED)
            else:
                self.state = State.AFTER
                self.timer = WAIT_AFTER
                returnvalue = HARD_PUNISH

        elif self.state == State.HIT:
            self.state = State.AFTER
            self.timer = WAIT_AFTER

        elif self.state == State.MISS: # ToDo: Continue after miss?
            self.state = State.AFTER
            self.timer = WAIT_AFTER

        elif self.state == State.AFTER:
            if self.timer > 0:
                self.timer -= 1
            else:
                self.counter += 1
                self.new_target()
        
        else:
            print("else?")

        return returnvalue



    def create_bullet_hole(self, x, y):
        
        returnvalue = 0
        
        if self.state == State.NEW:
            hits.append(Bullet_Hole(x, y, RED, HARD_PUNISH))
            returnvalue = HARD_PUNISH
        
        elif self.state == State.BEFORE_SHRINK:
            hits.append(Bullet_Hole(x, y, RED, HARD_PUNISH))
            returnvalue = HARD_PUNISH
        
        elif self.state == State.SHRINK:
            # calculate if hit or miss
            if math.sqrt((self.x - x)**2 + ( self.y - y)**2) <= self.radius:
                hits.append(Bullet_Hole(x, y, GREEN, int(self.radius)))
                self.state = State.HIT
                returnvalue = int(self.radius)

            else: # Miss
                hits.append(Bullet_Hole(x, y, RED, SOFT_PUNISH))
                self.state = State.MISS
                returnvalue = SOFT_PUNISH

        elif self.state == State.HIT:
            hits.append(Bullet_Hole(x, y, RED, HARD_PUNISH))
            returnvalue = HARD_PUNISH

        elif self.state == State.AFTER:
            hits.append(Bullet_Hole(x, y, RED, HARD_PUNISH))
            returnvalue = HARD_PUNISH

        else:
            print("create_bullet_hole - else?")

        return returnvalue



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




pygame.font.init()

font = pygame.font.Font(None, 36)
font_big = pygame.font.Font(None, 50)

screen = pygame.display.set_mode(SIZE)

hits=[]
players = []

for name in PlayerNames:
    players.append(Player(name))

        
def main():
    pygame.init()
    pygame.display.set_caption("FPShooter")
    clock = pygame.time.Clock()
    
    current_player = 0

    running = True
    game = True
    display_instructions = True
    highscore = True


    ########################## Instructions ##########################
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

    # ########################## GAME ##########################
    while running and game:
        screen.fill( WHITE )

        if players[current_player].target.counter == 0:
            next_player = font_big.render("Next Player: {}".format(players[current_player].name), True, BLACK)
            next_player_space = font.render("press Enter", True, BLACK)
            screen.blit(next_player, ( int(SIZE[0]/ 2 - next_player.get_width() /2), int(SIZE[1] / 2 - next_player.get_height() /2 )) )
            screen.blit(next_player_space, ( int(SIZE[0]/ 2 - next_player_space.get_width() /2), int((SIZE[1] / 2 - next_player_space.get_height() /2) + 35 )) )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_RETURN:
                        if players[current_player].target.counter == 0:
                            players[current_player].target.counter = 1


        elif players[current_player].target.counter < (NumberTargets + 1):
            pygame.draw.line(screen, GRAY, (int(SIZE[0]/2), 0), (int(SIZE[0]/2), int(SIZE[1]))) # Vertical and horizontal lines
            pygame.draw.line(screen, GRAY, (0, int(SIZE[1]/2)), (int(SIZE[0]), int(SIZE[1]/2)))
            players[current_player].update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_SPACE: # Random shot
                        x = random.randint(SIZE[0]*0.2, SIZE[0]*0.8)
                        y = random.randint(SIZE[0]*0.2, SIZE[0]*0.8)
                        players[current_player].create_bullet_hole(x, y)
                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = pygame.mouse.get_pos() # Mouse shot
                    players[current_player].create_bullet_hole(x, y)

        else:
            current_player += 1
            if current_player >= len(players):
                game = False

        # then draw all hits
        for hit in hits:
            if hit.duration > 0:
                hit.update()
            else:
                hits.remove(hit)


        clock.tick(100)
        pygame.display.flip()


    # ########################## HIGHSCORE ##########################
    while running and highscore:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                highscore = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    highscore = False
                    
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