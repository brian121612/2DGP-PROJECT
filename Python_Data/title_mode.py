import pygame

import game_framework
from pico2d import *
import manual_mode
import play_mode

image = None

def pause():
    pass

def resume():
    pass

def init():
    global image
    image = load_image('Building_Outside_1.png')


def finish():
    global image
    del image
    pass

def keybind_draw():
    draw_rectangle(1090,90,1210,160)
    font = load_font('ENCR10B.TTF', 25)
    font.draw(1105, 140, 'MANUAL', (255, 0, 0))
    font.draw(1100, 110, 'PRESS m', (255, 0, 0))


def update():
    pass


def draw():
    clear_canvas()
    image.draw(1280 // 2 , 720 // 2)
    keybind_draw()
    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_m:
            game_framework.push_mode(manual_mode)
        elif (event.type, event.key) == (SDL_KEYDOWN, SDLK_SPACE):
            game_framework.change_mode(play_mode)

