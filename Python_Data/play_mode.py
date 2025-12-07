import game_framework
from pico2d import *

import title_mode, item_mode
from reporter import Reporter
import game_world

background = None

class Background:
    def __init__(self):
        # 사용자가 제공한 'Building_Outside.png' 이미지를 로드합니다.
        self.floor = 1

        self.floor_1_x1 = 635
        self.floor_1_y1 = 515
        self.floor_1_x2 = 770
        self.floor_1_y2 = 695

        self.floor_2_x1 = 470
        self.floor_2_y1 = 485
        self.floor_2_x2 = 610
        self.floor_2_y2 = 695

        self.load_image()

        self.start_pos_floor_1 = (640, 100)
        self.start_pos_floor_2 = (540, 540)

        self.canvas_width, self.canvas_height = 1280, 720

        # (left, bottom, right, top)
        self.wall_colls = [
            # 왼쪽 상단 큰 벽
            (0, 360, 560, 720),
            # 오른쪽 상단 큰 벽
            (720, 360, 1280, 720),

            # 중앙 T자 복도 위쪽 벽
            (560, 360, 720, 570),  # 중앙 복도 상단 ㄷ자 모양의 위쪽 수평 부분

            # 하단 중앙 출입문 양옆 벽
            (560, 0, 720, 310)
        ]

    def load_image(self):
        if self.floor == 1:
            self.image = load_image('FLOOR_1.png')
        elif self.floor == 2:
            self.image = load_image('FLOOR_2.png')

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
    global reporter, background

    background = Background()
    game_world.add_object(background, 0)

    reporter = Reporter()
    reporter.x, reporter.y = background.start_pos_floor_1
    game_world.add_object(reporter, 1)




def update():
    game_world.update()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    game_world.clear()

