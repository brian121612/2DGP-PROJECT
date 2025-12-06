from pico2d import *
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_UP, SDLK_DOWN, SDLK_e

import game_world
import game_framework
from state_machine import StateMachine


def space_down(e): # e is space down ?
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

def e_down(e): # e is space down ?
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_e

def event_stop(e):
    return e[0] == 'STOP'

def event_run(e):
    return e[0] == 'RUN'

# Reporter Run Speed
PIXEL_PER_METER = (100.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 2.5  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# Reporter Action Speed
TIME_PER_ACTION = 1.0
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8



class Idle:

    def __init__(self, reporter):
        self.reporter = reporter

    def enter(self, e):
        if event_stop(e):
            self.reporter.face_dir = e[1]


    def exit(self, e):
        pass


    def do(self):
        self.reporter.frame = (self.reporter.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8

    def draw(self):
        self.reporter.image.clip_draw(int(self.reporter.frame) * 75, 300, 50, 100, self.reporter.x, self.reporter.y)


class Run:
    def __init__(self, reporter):
        self.reporter = reporter

    def enter(self, e):
        if self.reporter.x_dir != 0:
            self.reporter.face_dir = self.reporter.x_dir

    def exit(self, e):
        if space_down(e):
            pass

    def do(self):
        self.reporter.frame = (self.reporter.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8
        self.reporter.x += self.reporter.x_dir * RUN_SPEED_PPS * game_framework.frame_time
        self.reporter.y += self.reporter.y_dir * RUN_SPEED_PPS * game_framework.frame_time

    def draw(self):
        if self.reporter.x_dir == 0:
            if self.reporter.y_dir == 1:
                self.reporter.image.clip_draw(int(self.reporter.frame) * 75, 200, 50, 100, self.reporter.x, self.reporter.y)
            else:
                self.reporter.image.clip_draw(int(self.reporter.frame) * 75, 300, 50, 100, self.reporter.x, self.reporter.y)
        elif self.reporter.x_dir == 1:
            self.reporter.image.clip_draw(int(self.reporter.frame) * 75, 100, 50, 100, self.reporter.x, self.reporter.y)
        elif self.reporter.x_dir == -1:
            self.reporter.image.clip_draw(int(self.reporter.frame) * 75, 0, 50, 100, self.reporter.x,self.reporter.y)


class Reporter:
    def __init__(self):
        self.image = load_image('Player_Sheet.png')
        self.image2 = load_image('FlashLight_ON.png')
        self.image3 = load_image('FlashLight_OFF.png')

        self.x, self.y = 1280 // 2, 50
        self.frame = 0
        self.action = 0
        self.face_dir = 0
        self.x_dir = 0
        self.y_dir = 0

        self.flashlight = 0

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE : {space_down:self.IDLE,
                             event_run:self.RUN},

                self.RUN : {space_down:self.RUN,
                            event_stop:self.IDLE}
            }
        )

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_e:
            self.flashlight ^= 1
            return

        if event.key in (SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN):
            cur_xdir, cur_ydir = self.x_dir, self.y_dir
            if event.type == SDL_KEYDOWN:
                if event.key == SDLK_LEFT:
                    self.x_dir -= 1
                elif event.key == SDLK_RIGHT:
                    self.x_dir += 1
                elif event.key == SDLK_UP:
                    self.y_dir += 1
                elif event.key == SDLK_DOWN:
                    self.y_dir -= 1
            elif event.type == SDL_KEYUP:
                if event.key == SDLK_LEFT:
                    self.x_dir += 1
                elif event.key == SDLK_RIGHT:
                    self.x_dir -= 1
                elif event.key == SDLK_UP:
                    self.y_dir -= 1
                elif event.key == SDLK_DOWN:
                    self.y_dir += 1
            if cur_xdir != self.x_dir or cur_ydir != self.y_dir:  # 방향키에 따른 변화가 있으면
                if self.x_dir == 0 and self.y_dir == 0:  # 멈춤
                    self.state_machine.handle_state_event(('STOP', self.face_dir))  # 스탑 시 이전 방향 전달
                else:  # 움직임
                    self.state_machine.handle_state_event(('RUN', None))
        else:
            self.state_machine.handle_state_event(('INPUT', event))

    def get_bb(self):
        return self.x - 20, self.y - 50, self.x + 20, self.y + 50

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        if self.flashlight == 1:
            self.image2.draw(self.x - 5, self.y + 35)
        elif self.flashlight == 0:
            self.image3.draw(self.x, self.y + 25)

