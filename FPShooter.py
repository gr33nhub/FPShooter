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
import hmsysteme

###############################################################################
number_of_targets = 2  # Targets per player
number_of_rounds = 1  # Number of Rounds
###############################################################################

BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 191, 255)
RED = (255, 0, 0)


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



class GameInfo():
    def __init__(self, screen_size:list, number_of_rounds:int, number_of_targets:int, playernames:list, wait_enter=True):
        self.screen_size = screen_size
        self.number_of_rounds = number_of_rounds
        self.number_of_targets = number_of_targets
        self.playernames = playernames
        self.wait_enter = wait_enter

        self.hard_punish = 500
        self.soft_punish = 250

        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.font_big = pygame.font.Font(None, 50)


class App(GameInfo):

    def __init__(self, screen_size:list, number_of_rounds:int, number_of_targets:int, playernames:list, wait_enter=True):
        self.gameinfo = GameInfo(screen_size, number_of_rounds, number_of_targets, playernames, wait_enter)

        self.state = AppState.NEW
        self.done = False
        self.clock = pygame.time.Clock()
        self.fps = 20

        self.screen = pygame.display.set_mode(self.gameinfo.screen_size)
        self.screen_color = WHITE
        self.caption = ""

        self.players = []
        self.player_index = 0
        for name in self.gameinfo.playernames:
            self.players.append(Player(name, self.gameinfo, wait_enter=wait_enter))
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
        self.all_scores = []
        for player in self.players:
            for (no_target, no_round), target in player.targets.items():
                print("{}".format(player.name))
                print("{}".format(no_round))
                print("{}".format(no_target))
                self.all_scores.append([player.name, no_round, no_target, target.score])

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

        if hmsysteme.hit_detected():
            pos = hmsysteme.get_pos()
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
            instruction_text = self.gameinfo.font.render("Instruction Text", True, WHITE)
            self.screen.blit(instruction_text, [200, 200])

        elif self.state == AppState.GAME:
            self.player.draw(self.screen)

            name = self.player.name
            name_text = self.gameinfo.font.render("{}".format(name), True, BLACK, WHITE)
            self.screen.blit(name_text, [40, 100])

            score =self.player.score
            score_text = self.gameinfo.font.render("Punkte: {}".format(score), True, BLACK, WHITE)
            self.screen.blit(score_text, [40, self.gameinfo.screen_size[1]-100])            
        
        elif self.state == AppState.HIGHSCORE:
            for player in self.players:
                print(player)
                #print([ x.score for x in self.players[player].targets.values()])
                print(player.name)
                for (target_number, target_round), target in player.targets.items():
                    print("Runde {} Scheibe {}, Punkte: {}".format(target_number, target_round, target.score))
            

        pygame.display.flip() #nötig?

    def run(self):
        while not self.done:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            self.draw()
            pygame.display.update()


class Player():
    def __init__(self, name, gameinfo, wait_enter=True):
        self.gameinfo = gameinfo
        self.name = name
        self.state = PlayerState.RUNNING
        self.score = 0
        self.number_of_rounds = self.gameinfo.number_of_rounds
        self.number_of_targets = self.gameinfo.number_of_targets
        self.current_round = 0
        self.current_target = 0
        self.targets = {} # No. Target / Round

        for round_number in range(number_of_rounds):
            for target_number in range(number_of_targets):
                self.targets[round_number, target_number] = Target(gameinfo)

        self.target = self.targets[self.current_round, self.current_target]

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
                self.target = self.targets[self.current_round, self.current_target]
                self.state = PlayerState.RUNNING
            else:  # no more Targets -> Round Over
                self.state = PlayerState.NEXT_ROUND

        elif self.state == PlayerState.NEXT_ROUND:
            self.current_target = 0
            self.current_round += 1
            if self.current_round < self.number_of_rounds:  # next
                self.target = self.targets[self.current_round, self.current_target]
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
            player_1 = self.gameinfo.font_big.render("Player: {}".format(self.name), True, BLACK)
            player_2 = self.gameinfo.font.render("press Enter", True, BLACK)
            player_3 = self.gameinfo.font.render("or shoot", True, BLACK)
            x = self.gameinfo.screen_size[0]/ 2
            y = self.gameinfo.screen_size[1]/ 2
            screen.blit(player_1, ( int(x - player_1.get_width() /2), int(y - player_1.get_height() /2 )))
            screen.blit(player_2, ( int(x - player_2.get_width() /2), int((y- player_2.get_height() /2 ) + 35 )))
            screen.blit(player_3, ( int(x - player_3.get_width() /2), int((y - player_3.get_height() /2) + 65 )))

    def create_bullet_hole(self, xy):
        self.target.new_hole(xy)
        


class Target():

    def __init__(self, gameinfo):

        self.gameinfo = gameinfo

        self.radius_original = 400
        self.radius = self.radius_original

        self.time_before_shrink = 2000
        self.time_shrinking = 7000
        self.time_after = 2000
        self.time_screenshot = 500

        self.timer = self.time_before_shrink
        self.timer_screenshot = self.time_screenshot

        self.wait_enter = self.gameinfo.wait_enter 

        self.state = TargetState.NEW
        self.color = RED
        self.make_screenshot = False # timer starts, gets updated in update()
        self.print_screenshot = False  #makes the screenshot, needs screen, gets called by draw()

        self.x = random.randint(int(gameinfo.screen_size[0]*0.2), int(gameinfo.screen_size[0]*0.8))
        self.y = random.randint(int(gameinfo.screen_size[1]*0.2), int(gameinfo.screen_size[1]*0.8))
        self.score = 0

        self.holes = []


    def push_enter(self):
        self.wait_enter = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), int(self.radius), 0)

        current_radius = self.gameinfo.font.render("Radius: {:.0f}".format(self.radius), True, BLACK, WHITE)
        screen.blit(current_radius, [10, self.gameinfo.screen_size[1]-45])

        for hole in self.holes:
            hole.draw(screen)

        if self.print_screenshot:
            hmsysteme.take_screenshot(screen)
            self.print_screenshot = False

    
    def calculate_score(self):
        self.score = sum([ x.score for x in self.holes])

    def new_hole(self, xy):
        x, y = xy

        if self.state == TargetState.NEW:  # Hit while waiting for Enter (Return) Button
            self.state = TargetState.BEFORE_SHRINK
            self.timer = self.time_before_shrink
            #self.holes.append(Bullet_Hole(x, y, RED, self.gameinfo.hard_punish))

        elif self.state == TargetState.BEFORE_SHRINK:  # Hit before Target is black
            self.holes.append(Bullet_Hole(self.gameinfo, x, y, RED, self.gameinfo.hard_punish))
            self.state = TargetState.AFTER
            self.timer = self.time_after

        elif self.state == TargetState.SHRINK:  # Hit while shrinking
            # calculate if hit or miss
            if math.sqrt((self.x - x)**2 + (self.y - y)**2) <= self.radius:  # Hit
                self.holes.append(Bullet_Hole(self.gameinfo, x, y, GREEN, int(self.radius)))
            else:  # Miss
                self.holes.append(Bullet_Hole(self.gameinfo, x, y, RED, self.gameinfo.soft_punish))
            self.state = TargetState.AFTER
            self.timer = self.time_after

        elif self.state == TargetState.AFTER:
            self.holes.append(Bullet_Hole(self.gameinfo, x, y, RED, self.gameinfo.hard_punish))

        else:
            print("create_bullet_hole - else?")

        self.calculate_score()
        self.make_screenshot = True 
        


    def properties(self):
        target = namedtuple("target", ["state","x", "y", "radius"])
        return target(self.state, self.x, self.y, self.radius)

    def update(self, dt):

        if self.state == TargetState.NEW:
            if self.wait_enter:  # Wait for ENTER (Return) to be pushed
                pass
            else:
                self.wait_enter = True if self.gameinfo.wait_enter else False
                self.state = TargetState.BEFORE_SHRINK
                self.timer = self.time_before_shrink

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
                self.timer = self.time_shrinking

        elif self.state == TargetState.SHRINK:
            self.timer -= dt
            if self.timer > 0 - dt:
                self.radius = (self.timer / self.time_shrinking) * self.radius_original
                self.radius = 0 if self.radius < 0 else self.radius
                #print("dt: {}, timer: {:1.2f}, radius: {:1.2f}, andere: {:1.4f}".format(dt,self.timer, self.radius, 1-(TARGET_SHRINKING_TIME - self.timer)/TARGET_SHRINKING_TIME))
            else:
                self.state = TargetState.AFTER
                self.timer = self.time_after
                bullet_hole = Bullet_Hole(self.gameinfo, x=self.x, y=self.y, color=RED, score=self.gameinfo.hard_punish)
                self.holes.append(bullet_hole)
                #self.holes.append(Bullet_Hole(self.x, self.y, RED, self.gameinfo.hard_punish))

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

        if self.make_screenshot:
            self.timer_screenshot -= dt
            if self.timer_screenshot > 0:
                pass
            else:
                self.make_screenshot = False
                self.timer_screenshot = self.timer_screenshot
                self.print_screenshot = True
    

class Bullet_Hole():

    def __init__(self, gameinfo, x=0, y=0, color=RED, score=0):
        self.gameinfo = gameinfo
        self.original_radius = 25
        self.shrinking_time = 3000

        self.radius = self.original_radius
        self.timer = self.shrinking_time

        self.x, self.y = x, y

        self.color = color
        self.score = score
        self.score_position = 0
        self.display = True
        #print(self.__dict__)

    def update(self, dt):
        if self.display:
            if self.timer > 0:
                self.timer -= dt
                self.timer = 0 if self.timer < 0 else self.timer
                self.radius = ((self.timer / self.shrinking_time)) * self.original_radius
                self.score_position -= 0.5
            else:
                self.display = False 

    def draw(self, screen):
        if self.display:
            pygame.draw.circle(screen, self.color,(self.x, self.y), int(self.radius), 0)
            score_text = self.gameinfo.font.render("{}".format(self.score), True, self.color)
            screen.blit(score_text, [self.x + 10, self.y - 10 + int(self.score_position)])


def main():
    pygame.init()

    playernames = hmsysteme.get_playernames()
    if not (playernames):
        playernames = ["a", "b"]

    screen_size = hmsysteme.get_size()
    if not (screen_size):
        screen_size = [800, 800]

    app = App(screen_size, number_of_rounds, number_of_targets, playernames)
    app.run()

    pygame.quit()

if __name__ == "__main__":

    main()
