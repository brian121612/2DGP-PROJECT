import game_framework
from pico2d import *

import title_mode, item_mode
from reporter import Reporter
# from building_inside import Grass
import game_world

class Background:
    def __init__(self):
        # 사용자가 제공한 'Building_Outside.png' 이미지를 로드합니다.
        self.image = load_image('FLOOR_1.png')
        self.canvas_width, self.canvas_height = 1280, 720

    def draw(self):
        # 캔버스 중앙에 배경 이미지를 그립니다.
        self.image.draw(self.canvas_width // 2, self.canvas_height // 2)

    def update(self):
        # 배경은 움직이지 않으므로 update는 비워둡니다.
        pass

reporter = None

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

    background = Background()
    game_world.add_object(background, 0)

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

