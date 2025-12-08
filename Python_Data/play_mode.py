import game_framework
from pico2d import *

import title_mode
from reporter import Reporter
import game_world
from zombie import Zombie
import common

background = None

class Background:
    def __init__(self):
        # 사용자가 제공한 'Building_Outside.png' 이미지를 로드합니다.
        self.floor = 1

        self.stair_1_x1 = 635
        self.stair_1_y1 = 515
        self.stair_1_x2 = 770
        self.stair_1_y2 = 695

        self.stair_2_x1 = 470
        self.stair_2_y1 = 485
        self.stair_2_x2 = 610
        self.stair_2_y2 = 695



        self.load_image()

        self.start_pos_floor_1 = (705, 560)
        self.start_pos_floor_2 = (540, 535)

        self.start_pos_lab = (640, 30)

        self.canvas_width, self.canvas_height = 1280, 720


    def load_image(self):
        global reporter

        # 1. reporter가 None이면 기본 층 배경만 로드 (초기화 오류 방지)
        if reporter is None:
            if self.floor == 1:
                self.image = load_image('FLOOR_1.png')
            elif self.floor == 2:
                self.image = load_image('FLOOR_2.png')
            return

        # 2. reporter가 생성되었다면, lab 상태를 최우선으로 체크하여 방 배경 로드
        if reporter.lab == 11:
            self.image = load_image('Lab_F1_1.png')
        elif reporter.lab == 12:
            self.image = load_image('Lab_F1_2.png')
        elif reporter.lab == 13:
            self.image = load_image('Lab_F1_3.png')
        elif reporter.lab == 14:
            self.image = load_image('Lab_F1_4.png')
        elif reporter.lab == 21:
            self.image = load_image('Lab_F2_1.png')
        elif reporter.lab == 22:
            self.image = load_image('Lab_F2_2.png')
        elif reporter.lab == 23:
            self.image = load_image('Lab_F2_3.png')
        elif reporter.lab == 24:
            self.image = load_image('Lab_F2_4.png')
        # 3. lab 상태가 아니면 층별 배경 로드
        elif self.floor == 1:
            self.image = load_image('FLOOR_1.png')
        elif self.floor == 2:
            self.image = load_image('FLOOR_2.png')




    def draw(self):
        # 캔버스 중앙에 배경 이미지를 그립니다.
        self.image.draw(self.canvas_width // 2, self.canvas_height // 2)



    def update(self):
        # 배경은 움직이지 않으므로 update는 비워둡니다.
        self.load_image()

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
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE and reporter.main_door == 1 and reporter.lab == 0:
            game_framework.change_mode(title_mode)
            return
        else:
            reporter.handle_event(event)


def init():
    global reporter, background

    background = Background()
    game_world.add_object(background, 0)

    zombie = Zombie()
    game_world.add_object(zombie, 1)

    common.reporter = Reporter()
    reporter = common.reporter
    game_world.add_object(common.reporter, 2)




def update():
    game_world.update()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    game_world.clear()

