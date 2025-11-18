import game_framework
from pico2d import *

import title_mode

image = None
logo_start_time = 0.0

def pause():
    pass

def resume():
    pass

def init():
    global image, logo_start_time

    image = load_image('tuk_credit.png')
    logo_start_time = get_time()


def finish():
    global image
    del image
    pass


def update():
    # logo 모드가 2초 동안 지속되도록 한다.
    global logo_start_time

    if get_time() - logo_start_time > 1.0:
        game_framework.change_mode(title_mode)


def draw():
    clear_canvas()

    w = get_canvas_width()
    h = get_canvas_height()

    # 이미지를 캔버스 중앙에, 캔버스 크기(w, h)로 꽉 채워서 그립니다.
    image.draw(w // 2, h // 2, w, h)

    update_canvas()


def handle_events():

    events = get_events()

