from pico2d import *
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_UP, SDLK_DOWN

import game_world
from state_machine import StateMachine


def space_down(e): # e is space down ?
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

time_out = lambda e: e[0] == 'TIMEOUT'

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT






class Idle:

    def __init__(self, reporter):
        self.reporter = reporter

    def enter(self, e):
        self.reporter.wait_time = get_time()
        self.reporter.dir = 0


    def exit(self, e):
        if space_down(e):
            self.reporter.fire_ball()


    def do(self):
        self.reporter.frame = (self.reporter.frame + 1) % 8
        if get_time() - self.reporter.wait_time > 3:
            self.reporter.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        if self.reporter.face_dir == 1: # right
            self.reporter.image.clip_draw(self.reporter.frame * 50, 100, 100, 100, self.reporter.x, self.reporter.y)
        else: # face_dir == -1: # left
            self.reporter.image.clip_draw(self.reporter.frame * 50, 200, 100, 100, self.reporter.x, self.reporter.y)



class Run:
    def __init__(self, reporter):
        self.reporter = reporter

    def enter(self, e):
        if right_down(e) or left_up(e):
            self.reporter.dir = self.reporter.face_dir = 1
        elif left_down(e) or right_up(e):
            self.reporter.dir = self.reporter.face_dir = -1

    def exit(self, e):
        if space_down(e):
            self.reporter.fire_ball()

    def do(self):
        self.reporter.frame = (self.reporter.frame + 1) % 8
        self.reporter.x += self.reporter.dir * 5

    def draw(self):
        if self.reporter.face_dir == 1: # right
            self.reporter.image.clip_draw(self.reporter.frame * 50, 100, 100, 100, self.reporter.x, self.reporter.y)
        else: # face_dir == -1: # left
            self.reporter.image.clip_draw(self.reporter.frame * 50, 0, 100, 100, self.reporter.x, self.reporter.y)



class Reporter:
    def __init__(self):
        self.image = load_image('Player_Sheet_Fixed.png')

        self.frame_width = self.image.w / 8
        self.frame_height = self.image.h / 4

        self.x, self.y = 1536 // 2, 864 // 2
        self.frame = 0
        self.action = 0
        self.x_dir = 0
        self.y_dir = 0
        self.speed = 5
        self.frame_timer = 0.0
        self.last_time = get_time()
        self.frames_per_second = 10.0
        self.time_per_frame = 1.0 / self.frames_per_second

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_LEFT:
                self.x_dir = -1
                self.action = 1
            elif event.key == SDLK_RIGHT:
                self.x_dir = 1
                self.action = 2
            elif event.key == SDLK_UP:
                self.y_dir = 1
                self.action = 3
            elif event.key == SDLK_DOWN:
                self.y_dir = -1
                self.action = 0
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_LEFT and self.x_dir == -1:
                self.x_dir = 0
            elif event.key == SDLK_RIGHT and self.x_dir == 1:
                self.x_dir = 0
            elif event.key == SDLK_UP and self.y_dir == 1:
                self.y_dir = 0
            elif event.key == SDLK_DOWN and self.y_dir == -1:
                self.y_dir = 0

    def update(self):
        self.x += self.x_dir * self.speed
        self.y += self.y_dir * self.speed

        if self.x_dir != 0 or self.y_dir != 0:
            current_time = get_time()
            time_elapsed = current_time - self.last_time
            self.frame_timer += time_elapsed

            if self.frame_timer >= self.time_per_frame:
                self.frame = (self.frame + 1) % 8
                self.frame_timer -= self.time_per_frame

            self.last_time = current_time
        else:
            self.frame = 0
            self.last_time = get_time()

    def draw(self):
        self.image.clip_draw(
            int(self.frame * self.frame_width),
            int(self.action * self.frame_height),
            int(self.frame_width),
            int(self.frame_height),
            self.x,
            self.y
        )

