import pygame

import game_framework
from pico2d import *

import play_mode

image = None

def pause():
    pass

def resume():
    pass

def init():
    global image
    image = load_image('Building_Outside_2.png')


def finish():
    global image
    del image
    pass


def update():
    pass


def draw():
    clear_canvas()
    image.draw(1280 // 2 , 720 // 2)
    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif (event.type, event.key) == (SDL_KEYDOWN, SDLK_SPACE):
            game_framework.change_mode(play_mode)

