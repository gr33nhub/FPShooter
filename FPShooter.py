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
import hmsysteme


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
    STARTUP = 1
    INSTRUCTIONS = 2
    GAME = 3
    HIGHSCORE = 4
    QUIT_GAME = 5
    EXIT = 6


class GameInfo():
    def __init__(self, screen_size: list, number_of_rounds: int, number_of_targets: int, playernames: list, wait_enter=True):
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode(self.screen_size)

        self.number_of_rounds = number_of_rounds
        self.number_of_targets = number_of_targets

        self.playernames = playernames
        self.wait_enter = wait_enter
        self.hard_punish = 500
        self.soft_punish = 250

        self.delay = 120

        pygame.font.init()
        self.font = pygame.font.Font(None, 60)
        self.font_big = pygame.font.Font(None, 100)


class App():

    def __init__(self, gameinfo):
        self.gameinfo = gameinfo
        self.fps = 20

        self.state = AppState.STARTUP
        self.old_state = AppState.STARTUP
        self.clock = pygame.time.Clock()

        self.screen_color = WHITE
        self.caption = ""
        self.old_caption = None

        self.players = []
        self.player_index = 0
        for name in self.gameinfo.playernames:
            self.players.append(Player(name, self.gameinfo))
        self.player = self.players[self.player_index]

        self.all_scores = []

        self.next_state()

    def next_state(self):
        if self.state == AppState.STARTUP:
            self.state = AppState.INSTRUCTIONS
        elif self.state == AppState.INSTRUCTIONS:
            self.state = AppState.GAME
        elif self.state == AppState.GAME:
            self.state = AppState.HIGHSCORE
        elif self.state == AppState.HIGHSCORE:
            self.get_all_scores()
        else:
            print("App next_state else!?")

    def get_all_scores(self):  # ToDo
        for player in self.players:
            print("Player: {}".format(player.name))

            for (no_round, no_target), target in player.targets.items():
                print("Runde {} Scheibe {}, Punkte: {}".format(no_round + 1, no_target + 1, target.score))
                self.all_scores.append([player.name, no_round, no_target, target.score])

            print("Summe: {}".format(sum([target.score for a, target in player.targets.items()])))
            print("")

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                if self.state != AppState.QUIT_GAME:
                    self.old_state = self.state
                    self.state = AppState.QUIT_GAME
                else:
                    self.state = AppState.EXIT
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    if self.state != AppState.QUIT_GAME:
                        self.old_state = self.state
                        self.state = AppState.QUIT_GAME
                    else:
                        self.state = AppState.EXIT
                elif event.key == K_RETURN:
                    if self.state == AppState.INSTRUCTIONS:
                        self.next_state()

                    elif self.state == AppState.GAME:
                        self.player.push_enter()

                    elif self.state == AppState.HIGHSCORE:
                        self.next_state()

                    elif self.state == AppState.QUIT_GAME:
                        self.state = self.old_state

                    else:
                        pass
            elif event.type == MOUSEBUTTONUP:
                xy = pygame.mouse.get_pos()
                if self.state == AppState.GAME:
                    self.player.create_bullet_hole(xy)

        if hmsysteme.hit_detected():
            (x, y) = hmsysteme.get_pos()
            if self.state == AppState.GAME:
                self.player.create_bullet_hole((int(x), int(y)))

    def update(self, dt):

        if self.state == AppState.INSTRUCTIONS:
            pass

        elif self.state == AppState.GAME:

            self.player.update(dt)
            player_state = self.player.state

            if player_state == PlayerState.RUNNING:  # Player playing :)
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
                    self.next_state()

        elif self.state == AppState.HIGHSCORE:
            pass

    def draw(self):

        if self.state == AppState.INSTRUCTIONS:
            self.fps = 20
            self.screen_color = GRAY
            self.gameinfo.screen.fill(self.screen_color)
            self.caption = "Instructions"

            instruction_text = self.gameinfo.font.render("Instruction Text", True, WHITE)
            self.gameinfo.screen.blit(instruction_text, [200, 200])

        elif self.state == AppState.GAME:
            self.fps = 80
            self.screen_color = WHITE
            self.gameinfo.screen.fill(self.screen_color)
            self.caption = "Game"

            self.player.draw()

            name = self.player.name
            name_text = self.gameinfo.font.render("{}".format(name), True, BLACK, WHITE)
            self.gameinfo.screen.blit(name_text, [40, 100])

            score = self.player.score
            score_text = self.gameinfo.font.render("Punkte: {}".format(score), True, BLACK, WHITE)
            self.gameinfo.screen.blit(score_text, [40, self.gameinfo.screen_size[1] - 100])

        elif self.state == AppState.HIGHSCORE:
            self.fps = 20
            self.screen_color = GRAY
            self.gameinfo.screen.fill(self.screen_color)
            self.caption = "Highscore"

            x = self.gameinfo.screen_size[0] / 2

            offset = 0
            for player in self.players:
                name = self.gameinfo.font.render("Player: {}".format(player.name), True, BLACK)
                self.gameinfo.screen.blit(name, (int(x - name.get_width() / 2), int((name.get_height()) + offset)))

                offset += 50

                for (no_round, no_target), target in player.targets.items():

                    score = self.gameinfo.font.render("Runde {} Scheibe {}, Punkte: {}".format(no_round + 1 , no_target + 1, target.score), True, BLACK)
                    self.gameinfo.screen.blit(score, (int(x - score.get_width() / 2), int((score.get_height()) + offset)))

                    offset += 50

                summ = self.gameinfo.font.render("Summe: {}".format(sum([target.score for a, target in player.targets.items()])), True, BLACK)
                self.gameinfo.screen.blit(summ, (int(x - summ.get_width() / 2), int((summ.get_height()) + offset)))

                offset += 80

        elif self.state == AppState.QUIT_GAME:
            self.fps = 5
            self.screen_color = BLACK
            self.gameinfo.screen.fill(self.screen_color)
            self.caption = "Spiel beenden"
            text_quit_1 = self.gameinfo.font.render("Spiel wirklich beenden?", True, WHITE)
            text_quit_2 = self.gameinfo.font.render("Bestätigen mit Esc", True, WHITE)
            text_quit_3 = self.gameinfo.font.render("Zurück mit Enter", True, WHITE)

            self.gameinfo.screen.blit(text_quit_1, [200, 200])
            self.gameinfo.screen.blit(text_quit_2, [200, 200 + self.gameinfo.font.get_height() * 1.5])
            self.gameinfo.screen.blit(text_quit_3, [200, 200 + 2 * self.gameinfo.font.get_height() * 1.5])

        if self.caption != self.old_caption:
            self.old_caption = self.caption
            pygame.display.set_caption(self.caption)

    def run(self):
        while not self.state == AppState.EXIT:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            self.draw()
            pygame.display.update()


class Player():
    def __init__(self, name, gameinfo):
        self.gameinfo = gameinfo
        self.name = name
        self.state = PlayerState.RUNNING
        self.score = 0
        self.number_of_rounds = self.gameinfo.number_of_rounds
        self.number_of_targets = self.gameinfo.number_of_targets
        self.current_round = 0
        self.current_target = 0
        self.targets = {}  # No. Target / Round

        for round_number in range(self.number_of_rounds):
            for target_number in range(self.number_of_targets):
                self.targets[round_number, target_number] = Target(self.gameinfo)

        self.target = self.targets[self.current_round, self.current_target]

    def push_enter(self):
        self.target.push_enter()

    def update(self, dt):
        if self.state == PlayerState.NEW:
            pass

        elif self.state == PlayerState.RUNNING:
            self.target.update(dt)
            target = self.target.properties()

            self.score = sum([x.score for x in self.targets.values()])

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
            print("PlayerState Else?!")
            print(self.state)

    def draw(self):
        self.target.draw()

        if self.target.state == TargetState.NEW:
            player_1 = self.gameinfo.font_big.render("Player: {}".format(self.name), True, BLACK)
            player_2 = self.gameinfo.font.render("press Enter", True, BLACK)
            player_3 = self.gameinfo.font.render("or shoot", True, BLACK)
            x = self.gameinfo.screen_size[0] / 2
            y = self.gameinfo.screen_size[1] / 2
            self.gameinfo.screen.blit(player_1, (int(x - player_1.get_width() / 2), int(y - player_1.get_height() / 2)))
            self.gameinfo.screen.blit(player_2, (int(x - player_2.get_width() / 2), int((y - player_2.get_height() / 2) + 75)))
            self.gameinfo.screen.blit(player_3, (int(x - player_3.get_width() / 2), int((y - player_3.get_height() / 2) + 150)))

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
        self.make_screenshot = False  # timer starts, gets updated in update()

        self.x = random.randint(int(gameinfo.screen_size[0] * 0.4), int(gameinfo.screen_size[0] * 0.6))
        self.y = random.randint(int(gameinfo.screen_size[1] * 0.4), int(gameinfo.screen_size[1] * 0.6))
        self.score = 0

        self.holes = []

    def push_enter(self):
        self.wait_enter = False

    def draw(self):
        pygame.draw.circle(self.gameinfo.screen, self.color, (self.x, self.y), int(self.radius), 0)

        current_radius = self.gameinfo.font.render("Radius: {:.0f}".format(self.radius), True, BLACK, WHITE)
        self.gameinfo.screen.blit(current_radius, [10, self.gameinfo.screen_size[1] - 45])

        for hole in self.holes:
            hole.draw()

    def calculate_score(self):
        self.score = sum([x.score for x in self.holes])

    def new_hole(self, xy):

        if self.state == TargetState.NEW:  # Hit while waiting for Enter (Return) Button
            self.state = TargetState.BEFORE_SHRINK
            self.timer = self.time_before_shrink

        elif self.state == TargetState.BEFORE_SHRINK:  # Hit before Target is black
            self.holes.append(Bullet_Hole(self.gameinfo, xy, RED, self.gameinfo.hard_punish))
            self.state = TargetState.AFTER
            self.timer = self.time_after

        elif self.state == TargetState.SHRINK:  # Hit while shrinking
            # calculate if hit or miss
            x, y = xy
            additional = int((self.gameinfo.delay / self.time_shrinking) * self.radius_original)
            print("Radius {} Timer {}".format(self.radius, self.timer))

            if math.sqrt((self.x - x)**2 + (self.y - y)**2) <= (self.radius + additional):  # Hit
                self.holes.append(Bullet_Hole(self.gameinfo, xy, GREEN, int(self.radius) + additional))
                self.radius += additional
            else:  # Miss
                self.holes.append(Bullet_Hole(self.gameinfo, xy, RED, self.gameinfo.soft_punish))
            self.state = TargetState.AFTER
            self.timer = self.time_after

        elif self.state == TargetState.AFTER:
            self.holes.append(Bullet_Hole(self.gameinfo, xy, RED, self.gameinfo.hard_punish))

        else:
            print("create bullet hole - else?")

        self.calculate_score()
        self.make_screenshot = True

    def properties(self):
        target = namedtuple("target", ["state", "x", "y", "radius"])
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
                self.color = (self.timer / 2000 * 254, 0, 0)
            else:
                self.state = TargetState.SHRINK
                self.color = BLACK
                self.timer = self.time_shrinking

        elif self.state == TargetState.SHRINK:
            self.timer -= dt
            if self.timer > -(self.gameinfo.delay) - dt:
                self.radius = (self.timer / self.time_shrinking) * self.radius_original
                self.radius = 0 if self.radius <= 0 else self.radius
                #print("dt: {}, timer: {:1.2f}, radius: {:1.2f}, andere: {:1.4f}".format(dt,self.timer, self.radius, 1-(TARGET_SHRINKING_TIME - self.timer)/TARGET_SHRINKING_TIME))
            else:
                self.state = TargetState.AFTER
                self.timer = self.time_after
                bullet_hole = Bullet_Hole(self.gameinfo, xy=(self.x, self.y), color=RED, score=self.gameinfo.hard_punish)
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
                hmsysteme.take_screenshot(self.gameinfo.screen)


class Bullet_Hole():

    def __init__(self, gameinfo, xy=(0, 0), color=RED, score=0):
        self.gameinfo = gameinfo
        self.original_radius = 25
        self.shrinking_time = 3000

        self.radius = self.original_radius
        self.timer = self.shrinking_time

        (self.x, self.y) = xy

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

    def draw(self):
        if self.display:
            pygame.draw.circle(self.gameinfo.screen, self.color, (self.x, self.y), int(self.radius), 0)
            score_text = self.gameinfo.font.render("{}".format(self.score), True, self.color)
            self.gameinfo.screen.blit(score_text, [self.x + 10, self.y - 10 + int(self.score_position)])


def main():
    pygame.init()

    playernames = hmsysteme.get_playernames()
    if not playernames:
        playernames = ["a", "b"]

    screen_size = hmsysteme.get_size()
    if not screen_size:
        screen_size = [300, 300]

    number_of_targets = 2  # Targets per player
    number_of_rounds = 1  # Number of Rounds
    wait_enter = True     # Wait for enter button to be pushed

    gameinfo = GameInfo(screen_size, number_of_rounds, number_of_targets, playernames, wait_enter)

    app = App(gameinfo)
    app.run()

    pygame.quit()


if __name__ == "__main__":
    main()
