import pygame
from pygame.constants import (
    MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT, KEYDOWN, KEYUP, K_ESCAPE, K_RETURN
)
import random
import math
from enum import Enum

###############################################################################
PlayerNames = ["Gonnie", "Python"]
number_of_targets = 1  # Targets per player
number_of_rounds = 2  # Number of Rounds
WAIT_ENTER = False
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

WAIT_BEFORE_SHRINK = 200
WAIT_AFTER = 50
SHRINKING_TIME = 1000
SHRINKING_SPEED = 180  # More is faster
TARGET_RADIUS = 400.0

HIT_RADIUS = 8
HIT_DURATION = 85


class TargetState(Enum):  # State for Target
    NEW = 1
    BEFORE_SHRINK = 2
    SHRINK = 3
    AFTER = 4
    HIT = 5
    MISS = 6
    EXIT = 9


class PlayerState(Enum):  # State for Target
    NEW = 1
    RUNNING = 2
    TARGET_OVER = 3
    ROUND_OVER = 4
    WAIT_NEXT_ROUND = 5
    GAME_OVER = 6


class AppState(Enum):
    NEW = 1
    INSTRUCTIONS = 2
    GAME = 3
    HIGHSCORE = 4

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
                self.targets[target_number, round_number]= Target()

        self.target = self.targets[0, 0]

    def hit_enter(self):
        self.target.hit_enter()

    def update(self, dt):
        if self.state == PlayerState.RUNNING:
            self.target.update(dt)
            target_state = self.target.state
            self.score = sum([ x.score for x in self.targets.values()])

            if target_state == TargetState.EXIT:
                self.state = PlayerState.TARGET_OVER

        elif self.state == PlayerState.TARGET_OVER:
            self.current_target += 1
            if self.current_target < self.number_of_targets:  # next Target -> Running
                self.target = self.targets[self.current_target, self.current_round]
                self.state = PlayerState.RUNNING
            else:  # no more Targets -> Round Over
                self.state = PlayerState.ROUND_OVER

        elif self.state == PlayerState.ROUND_OVER:
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

    def create_bullet_hole(self, x, y):
        self.target.create_bullet_hole(x, y)

    def draw(self, screen):
        self.target.draw(screen)


class Target():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.hits = []
        self.new_target()
        self.wait_enter = True if WAIT_ENTER else False
        self.score = 0

    def new_target(self):
        self.x = random.randint(int(SIZE[0]*0.1), int(SIZE[0]*0.9))
        self.y = random.randint(int(SIZE[1]*0.1), int(SIZE[1]*0.9))
        self.state = TargetState.NEW
        self.timer = WAIT_BEFORE_SHRINK
        self.radius = TARGET_RADIUS
        self.color = RED

    def hit_enter(self):
        self.wait_enter = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), int(self.radius), 0)

        current_radius = font.render("Radius: {:.0f}".format(self.radius), True, BLACK, WHITE)
        screen.blit(current_radius, [10, SIZE[1]-45])

    def update(self, dt):
        if self.state == TargetState.NEW:
            if not self.wait_enter:
                self.wait_enter = True if WAIT_ENTER else False
                self.state = TargetState.BEFORE_SHRINK
                self.timer = WAIT_BEFORE_SHRINK

        elif self.state == TargetState.BEFORE_SHRINK:
            if self.timer > 0:
                self.timer -= dt
                self.timer = 0 if self.timer < 0 else self.timer
                if self.timer > 1500:
                    self.color = RED
                else:
                    self.color = (self.timer/1500*254, 0, 0)
            else:
                self.state = TargetState.SHRINK
                self.color = BLACK
                self.timer = SHRINKING_TIME

        elif self.state == TargetState.SHRINK:
            if self.timer > 0:
                self.timer -= dt
                self.timer = 0 if self.timer < 0 else self.timer
                self.radius = ((self.timer / SHRINKING_TIME)) * TARGET_RADIUS
                # print("timer: {:1.2f}, radius: {:1.2f}, andere: {:1.4f}".format(self.timer, self.radius, 1-(SHRINKING_TIME - self.timer)/SHRINKING_TIME))
            else:
                self.state = TargetState.AFTER
                self.timer = WAIT_AFTER
                self.score += HARD_PUNISH

        elif self.state == TargetState.HIT:
            self.state = TargetState.AFTER
            self.timer = WAIT_AFTER

        elif self.state == TargetState.MISS:  # ToDo: Continue after miss?
            self.state = TargetState.AFTER
            self.timer = WAIT_AFTER

        elif self.state == TargetState.AFTER:
            if self.timer > 0:
                self.timer -= dt
            else:
                self.state = TargetState.EXIT

        elif self.state == TargetState.EXIT:
            pass

        else:
            print("else?")


    def create_bullet_hole(self, x, y):

        if self.state == TargetState.NEW:
            hits.append(Bullet_Hole(x, y, RED, HARD_PUNISH))
            self.score += HARD_PUNISH

        elif self.state == TargetState.BEFORE_SHRINK:
            hits.append(Bullet_Hole(x, y, RED, HARD_PUNISH))
            self.score += HARD_PUNISH

        elif self.state == TargetState.SHRINK:
            # calculate if hit or miss
            if math.sqrt((self.x - x)**2 + (self.y - y)**2) <= self.radius:
                hits.append(Bullet_Hole(x, y, GREEN, int(self.radius)))
                self.state = TargetState.HIT
                self.score += int(self.radius)

            else:  # Miss
                hits.append(Bullet_Hole(x, y, RED, SOFT_PUNISH))
                self.state = TargetState.MISS
                self.score += SOFT_PUNISH

        elif self.state == TargetState.HIT:
            hits.append(Bullet_Hole(x, y, RED, HARD_PUNISH))
            self.score += HARD_PUNISH

        elif self.state == TargetState.AFTER:
            hits.append(Bullet_Hole(x, y, RED, HARD_PUNISH))
            self.score += HARD_PUNISH

        else:
            print("create_bullet_hole - else?")


class Bullet_Hole():
    def __init__(self, x, y, color, score):
        self.x = x
        self.y = y
        self.radius = HIT_RADIUS
        self.duration = HIT_DURATION
        self.color = color
        self.score = score
        self.score_position = 0

    def update(self, screen):
        if self.duration < HIT_RADIUS:
            self.radius = self.duration
        pygame.draw.circle(screen, self.color,
                           (self.x, self.y), int(self.radius), 0)
        score_text = font.render("{}".format(self.score), True, self.color)
        screen.blit(score_text, [self.x + 10, self.y -
                                 10 + int(self.score_position)])
        self.duration -= 1
        self.score_position -= 0.5






class App():
    def __init__(self, screen_size, number_of_targets, number_of_rounds):
        self.state = AppState.NEW
        self.done = False
        self.clock = pygame.time.Clock()
        self.fps = 20
        self.screen = pygame.display.set_mode((screen_size[0], screen_size[1]))
        self.screen_color = WHITE
        self.caption = ""

        self.players = {}
        self.player_index = 0
        self.current_player = PlayerNames[self.player_index]
        for name in PlayerNames:
            self.players[name] = Player(name, number_of_targets, number_of_rounds)
        self.player = self.players[self.current_player]
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
        elif self.state == AppState.HIGHSCORE:
            self.done = True
        else:
            print("App nextState else!?")
        pygame.display.set_caption(self.caption)


    def get_all_scores(self):
        self.all_scores = {}
        for player in self.players:
            self.all_scores[player] = self.players[player].targets

        print(self.all_scores)


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
                    if self.state == AppState.GAME:
                        self.player.hit_enter()
                    if self.state == AppState.HIGHSCORE:
                        self.nextState()
            elif event.type == MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                print(pos)

    def update(self, dt):

        if self.state == AppState.INSTRUCTIONS:
            pass

        elif self.state == AppState.GAME:

            self.player.update(dt)
            player_state = self.player.state

            if player_state == PlayerState.RUNNING: # Player playing :)
                pass

            elif player_state == PlayerState.TARGET_OVER:  # one Targets gone
                pass

            elif player_state == PlayerState.ROUND_OVER:  # Round over / next Player
                self.player_index += 1
                
                if self.player_index < len(self.players):
                    self.current_player = PlayerNames[self.player_index]
                    self.player = self.players[self.current_player]

                else:  # no more Players / next Round
                    self.player_index = 0
                    self.current_player = PlayerNames[self.player_index]
                    self.player = self.players[self.current_player]

            elif player_state == PlayerState.WAIT_NEXT_ROUND:  # All Players have played, new Round, activate Player
                self.player.state = PlayerState.RUNNING

            elif player_state == PlayerState.GAME_OVER:  # Player done, next player or Quit()
                self.player_index += 1
                
                if self.player_index < len(self.players):
                    self.current_player = PlayerNames[self.player_index]
                    self.player = self.players[self.current_player]

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
            name = self.player.name
            name_text = font.render("{}".format(name), True, BLACK, WHITE)
            self.screen.blit(name_text, [10, 10])

            score =self.player.score
            score_text = font.render("Punkte: {}".format(score), True, BLACK, WHITE)
            self.screen.blit(score_text, [10, SIZE[1]-20])

            self.player.draw(self.screen)
        
        elif self.state == AppState.HIGHSCORE:
            """
            for t in self.score:
                print(f"Runde {t[0]} Scheibe {t[1]}, Punkte: {self.score[t].score}")
            """

        pygame.display.flip() #nötig?

    def run(self):
        while not self.done:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            self.draw()
            pygame.display.update()



"""next_player = font_big.render("Next Player: {}".format(players[current_player].name), True, BLACK)
next_player_space = font.render("press Enter", True, BLACK)
screen.blit(next_player, ( int(SIZE[0]/ 2 - next_player.get_width() /2), int(SIZE[1] / 2 - next_player.get_height() /2 )) )
screen.blit(next_player_space, ( int(SIZE[0]/ 2 - next_player_space.get_width() /2), int((SIZE[1] / 2 - next_player_space.get_height() /2) + 35 )) )
"""


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
