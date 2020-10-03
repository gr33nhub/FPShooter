import pygame
from pygame.constants import (
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    QUIT,
    KEYDOWN,
    KEYUP,
    K_ESCAPE,
    K_RETURN
)
import random
import math
from enum import IntEnum
from collections import namedtuple
import itertools

###############################################################################
PlayerNames = ["Gonnie", "Python"]
number_of_targets = 3  # Targets per player
number_of_rounds = 1  # Number of Rounds
WAIT_ENTER = True
###############################################################################

BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 191, 255)
RED = (255, 0, 0)

SIZE = (500, 500)

HARD_PUNISH = 500  # 1000
SOFT_PUNISH = 250

TARGET_RADIUS = 400.0
TARGET_WAIT_BEFORE_SHRINK = 2000
TARGET_SHRINKING_TIME = 7000
TARGET_WAIT_AFTER = 2000

HOLE_RADIUS = 8
HOLE_SHRINIKNG_TIME = 2000

class TargetState(IntEnum):  # State for Target
    NEW = 1
    BEFORE_SHRINK = 2
    SHRINK = 3
    AFTER = 4
    EXIT = 5

class PlayerState(IntEnum):  # State for Target
    NEW = 1
    RUNNING = 2
    NEXT_TARGET = 3
    NEXT_ROUND = 4
    WAIT_NEXT_ROUND = 5
    GAME_OVER = 6

class AppState(IntEnum):
    NEW = 1
    INSTRUCTIONS = 2
    GAME = 3
    HIGHSCORE = 4


class App():

    def __init__(self, screen_size, number_of_targets, number_of_rounds):
        self.state = AppState.NEW
        self.done = False
        self.clock = pygame.time.Clock()
        self.fps = 20
        self.screen = pygame.display.set_mode((screen_size[0], screen_size[1]))
        self.screen_color = WHITE
        self.caption = ""

        self.players = []
        self.player_index = 0
        for name in PlayerNames:
            self.players.append(Player(name, number_of_targets, number_of_rounds))
        self.player = self.players[self.player_index]
        self.nextState()

    def nextState(self):
        if self.state == AppState.NEW:
            self.state = AppState.INSTRUCTIONS
            self.screen_color = GRAY
            self.caption = "Instructions"
            self.fps = 20
        elif self.state == AppState.INSTRUCTIONS:
            self.state = AppState.GAME
            self.screen_color = WHITE
            self.caption = "Game"
            self.fps = 80
        elif self.state == AppState.GAME:
            self.state = AppState.HIGHSCORE
            self.screen_color = GRAY
            self.caption = "Highscore"
            self.fps = 20
            self.get_all_scores()
        elif self.state == AppState.HIGHSCORE:
            self.done = True
        else:
            print("App nextState else!?")
        pygame.display.set_caption(self.caption)


    def get_all_scores(self): #ToDo
        self.all_scores = {}
        for player in self.players:
            a = player.get_allscores()
            #self.all_scores[player.name] = player.targets

        print(self.all_scores)

    def create_bullet_hole(self, xy):
        if self.state == AppState.GAME:
            self.player.create_bullet_hole(xy)

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.done = True
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    self.done = True
                elif event.key == K_RETURN:
                    if self.state == AppState.INSTRUCTIONS:
                        self.nextState()

                    elif self.state == AppState.GAME:
                        self.player.push_enter()

                    elif self.state == AppState.HIGHSCORE:
                        self.nextState()
                    
                    else:
                        pass
            elif event.type == MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                self.create_bullet_hole(pos)

    def update(self, dt):

        if self.state == AppState.INSTRUCTIONS:
            pass

        elif self.state == AppState.GAME:

            self.player.update(dt)
            player_state = self.player.state

            if player_state == PlayerState.RUNNING: # Player playing :)
                pass

            elif player_state == PlayerState.NEXT_TARGET:  # one Targets gone
                pass

            elif player_state == PlayerState.NEXT_ROUND:  # Round over / next Player
                self.player_index += 1
                
                if self.player_index < len(self.players):
                    self.player = self.players[self.player_index]


                else:  # no more Players / next Round
                    self.player_index = 0
                    self.player = self.players[self.player_index]


            elif player_state == PlayerState.WAIT_NEXT_ROUND:  # All Players have played, new Round, activate Player
                self.player.state = PlayerState.RUNNING

            elif player_state == PlayerState.GAME_OVER:  # Player done, next player or Quit()
                self.player_index += 1
                
                if self.player_index < len(self.players):
                    self.player = self.players[self.player_index]

                else:  # Quit
                    self.nextState()
                    
        elif self.state == AppState.HIGHSCORE:
            pass

    def draw(self):
        self.screen.fill(self.screen_color)

        if self.state == AppState.INSTRUCTIONS:
            instruction_text = font.render("Instruction Text", True, WHITE)
            self.screen.blit(instruction_text, [10, 10])

        elif self.state == AppState.GAME:
            self.player.draw(self.screen)

            name = self.player.name
            name_text = font.render("{}".format(name), True, BLACK, WHITE)
            self.screen.blit(name_text, [10, 10])

            score =self.player.score
            score_text = font.render("Punkte: {}".format(score), True, BLACK, WHITE)
            self.screen.blit(score_text, [10, SIZE[1]-20])            
        
        elif self.state == AppState.HIGHSCORE:
            for player in self.players:
                print(player)
                #print([ x.score for x in self.players[player].targets.values()])
                print(player.name)
                for (target_number, target_round), target in player.targets.items():
                    print(f"Runde {target_number} Scheibe {target_round}, Punkte: {target.score }")
            

        pygame.display.flip() #nötig?

    def run(self):
        while not self.done:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            self.draw()
            pygame.display.update()


class Player():
    def __init__(self, name, number_of_targets=0, number_of_rounds=0):
        self.name = name
        self.number_of_targets = number_of_targets
        self.number_of_rounds = number_of_rounds
        self.current_target = 0
        self.current_round = 0
        self.score = 0
        self.targets = {}
        self.state = PlayerState.RUNNING

        for target_number in range(number_of_targets):
            for round_number in range(number_of_rounds):
                self.targets[target_number, round_number] = Target()

        self.target = self.targets[0, 0]

    def push_enter(self):
        self.target.push_enter()

    def update(self, dt):
        if self.state == PlayerState.NEW:
            pass

        elif self.state == PlayerState.RUNNING:
            self.target.update(dt)
            target = self.target.properties()

            self.score = sum([ x.score for x in self.targets.values()])
            
            if target.state == TargetState.EXIT:
                self.state = PlayerState.NEXT_TARGET

        elif self.state == PlayerState.NEXT_TARGET:
            self.current_target += 1
            if self.current_target < self.number_of_targets:  # next Target -> Running
                self.target = self.targets[self.current_target, self.current_round]
                self.state = PlayerState.RUNNING
            else:  # no more Targets -> Round Over
                self.state = PlayerState.NEXT_ROUND

        elif self.state == PlayerState.NEXT_ROUND:
            self.current_target = 0
            self.current_round += 1
            if self.current_round < self.number_of_rounds:  # next
                self.target = self.targets[self.current_target, self.current_round]
                self.state = PlayerState.WAIT_NEXT_ROUND
            else:
                self.state = PlayerState.GAME_OVER

        elif self.state == PlayerState.WAIT_NEXT_ROUND:
            pass  # wait for reset to Running

        elif self.state == PlayerState.GAME_OVER:
            pass

        else:
            print("PlayerState Else?")
            print(self.state)
        

    def draw(self, screen):
        self.target.draw(screen)
        
        if self.target.state == TargetState.NEW:
            player_1 = font_big.render(f"Player: {self.name}", True, BLACK)
            player_2 = font.render("press Enter", True, BLACK)
            player_3 = font.render("or shoot", True, BLACK)
            screen.blit(player_1, ( int(SIZE[0]/ 2 - player_1.get_width() /2), int(SIZE[1] / 2 - player_1.get_height() /2 )) )
            screen.blit(player_2, ( int(SIZE[0]/ 2 - player_2.get_width() /2), int((SIZE[1] / 2 - player_2.get_height() /2) + 35 )) )
            screen.blit(player_3, ( int(SIZE[0]/ 2 - player_3.get_width() /2), int((SIZE[1] / 2 - player_3.get_height() /2) + 65 )) )

    def create_bullet_hole(self, xy):
        self.target.new_hole(xy)
        


class Target():

    def __init__(self):
        self.number = next(itertools.count())
        self.x = 0
        self.y = 0
        self.new_target()
        self.wait_enter = True if WAIT_ENTER else False
        self.score = 0
        self.holes = []
        
    def new_target(self):
        self.x = random.randint(int(SIZE[0]*0.1), int(SIZE[0]*0.9))
        self.y = random.randint(int(SIZE[1]*0.1), int(SIZE[1]*0.9))
        self.state = TargetState.NEW
        self.timer = TARGET_WAIT_BEFORE_SHRINK
        self.radius = TARGET_RADIUS
        self.color = RED

    def push_enter(self):
        self.wait_enter = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), int(self.radius), 0)

        current_radius = font.render("Radius: {:.0f}".format(self.radius), True, BLACK, WHITE)
        screen.blit(current_radius, [10, SIZE[1]-45])

        for hole in self.holes:
            hole.draw(screen)
    
    def calculate_score(self):
        self.score = sum([ x.score for x in self.holes])

    def new_hole(self, xy):
        x, y = xy

        if self.state == TargetState.NEW:  # Hit while waiting for Enter (Return) Button
            self.state = TargetState.BEFORE_SHRINK
            self.timer = TARGET_WAIT_BEFORE_SHRINK
            #self.holes.append(Bullet_Hole(x, y, RED, HARD_PUNISH))

        elif self.state == TargetState.BEFORE_SHRINK:  # Hit before Target is black
            self.holes.append(Bullet_Hole(x, y, RED, HARD_PUNISH))
            self.state = TargetState.AFTER
            self.timer = TARGET_WAIT_AFTER

        elif self.state == TargetState.SHRINK:  # Hit while shrinking
            # calculate if hit or miss
            if math.sqrt((self.x - x)**2 + (self.y - y)**2) <= self.radius:  # Hit
                self.holes.append(Bullet_Hole(x, y, GREEN, int(self.radius)))
            else:  # Miss
                self.holes.append(Bullet_Hole(x, y, RED, SOFT_PUNISH))
            self.state = TargetState.AFTER
            self.timer = TARGET_WAIT_AFTER

        elif self.state == TargetState.AFTER:
            self.holes.append(Bullet_Hole(x, y, RED, HARD_PUNISH))


        else:
            print("create_bullet_hole - else?")

        self.calculate_score()


    def properties(self):
        target = namedtuple("target", ["number","state","x", "y", "radius"])
        return target(self.number, self.state, self.x, self.y, self.radius)

    def update(self, dt):
        if self.state == TargetState.NEW:
            if self.wait_enter:  # Wait for ENTER (Return) to be pushed
                pass
            else:
                self.wait_enter = True if WAIT_ENTER else False
                self.state = TargetState.BEFORE_SHRINK
                self.timer = TARGET_WAIT_BEFORE_SHRINK

        elif self.state == TargetState.BEFORE_SHRINK:
            self.timer -= dt
            if self.timer > 0:
                if self.timer > 1500:
                    self.color = RED
                else:
                    self.color = (self.timer/1500*254, 0, 0)
            else:
                self.state = TargetState.SHRINK
                self.color = BLACK
                self.timer = TARGET_SHRINKING_TIME

        elif self.state == TargetState.SHRINK:
            self.timer -= dt
            if self.timer > 0 - dt:
                self.radius = (self.timer / TARGET_SHRINKING_TIME) * TARGET_RADIUS
                self.radius = 0 if self.radius < 0 else self.radius
                #print("dt: {}, timer: {:1.2f}, radius: {:1.2f}, andere: {:1.4f}".format(dt,self.timer, self.radius, 1-(TARGET_SHRINKING_TIME - self.timer)/TARGET_SHRINKING_TIME))
            else:
                self.state = TargetState.AFTER
                self.timer = TARGET_WAIT_AFTER
                self.holes.append(Bullet_Hole(self.x, self.y, RED, HARD_PUNISH))

        elif self.state == TargetState.AFTER:
            self.timer -= dt
            if self.timer > 0:
                pass
            else:
                self.state = TargetState.EXIT
                for hole in self.holes:
                    hole.display = False

        elif self.state == TargetState.EXIT:
            pass

        else:
            print("else?")

        for hole in self.holes:
            hole.update(dt)

        self.calculate_score()
    

class Bullet_Hole():
    def __init__(self, x, y, color, score):
        self.x = x
        self.y = y
        self.radius = HOLE_RADIUS
        self.timer = HOLE_SHRINIKNG_TIME
        self.color = color
        self.score = score
        self.score_position = 0
        self.display = True

    def update(self, dt):
        if self.display:
            if self.timer > 0:
                self.timer -= dt
                self.timer = 0 if self.timer < 0 else self.timer
                self.radius = ((self.timer / HOLE_SHRINIKNG_TIME)) * HOLE_RADIUS
                self.score_position -= 0.5
            else:
                self.display = False 

    def draw(self, screen):
        if self.display:
            pygame.draw.circle(screen, self.color,(self.x, self.y), int(self.radius), 0)
            score_text = font.render("{}".format(self.score), True, self.color)
            screen.blit(score_text, [self.x + 10, self.y - 10 + int(self.score_position)])





def main():
    pygame.init()

    app = App(SIZE, number_of_targets, number_of_rounds)
    app.run()

    pygame.quit()


"""
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

"""

if __name__ == "__main__":
    pygame.font.init()

    font = pygame.font.Font(None, 36)
    font_big = pygame.font.Font(None, 50)

    main()

def game():
    main()