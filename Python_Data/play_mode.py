import game_framework
from pico2d import *

import title_mode, item_mode
from reporter import Reporter
# from building_inside import Grass
import game_world

boy = None

def pause():
    pass

def resume():
    pass


def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_i:
            game_framework.push_mode(item_mode)
        else:
            reporter.handle_event(event)

def init():
    global reporter

    #grass = Grass()
    #game_world.add_object(grass, 0)

    reporter = Reporter()
    game_world.add_object(reporter, 1)


def update():
    game_world.update()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    game_world.clear()

