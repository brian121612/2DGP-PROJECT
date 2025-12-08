from pico2d import *
from sdl2 import SDL_KEYDOWN, SDLK_ESCAPE, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_UP, SDLK_DOWN, SDLK_e, SDLK_f

import game_world
import game_framework
from state_machine import StateMachine
import play_mode
import common


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

        self.font = load_font('ENCR10B.TTF', 16)

        self.start_x, self.start_y = 1280 // 2 - 25, 50
        self.x, self.y = self.start_x, self.start_y
        self.frame = 0
        self.action = 0
        self.face_dir = 0
        self.x_dir = 0
        self.y_dir = 0

        self.flashlight = 0

        # 계단 충돌
        self.he_is = 0
        # 문 충돌
        self.enter_door = 0
        # 정문
        self.main_door = 0
        # 연구실
        self.lab = 0
        self.lab_exit = 0
        self.last_entered_door = 0

        self.bgm = load_music('2DGP_BGM.mp3')
        self.bgm.set_volume(64)
        self.bgm.repeat_play()

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


    def handle_collision(self):
        if self.lab != 0:
            return

        # 이동 가능 영역 규칙 (FLOOR 1 기준)
        allowed = False

        # 기본 벽 충돌
        if play_mode.background.floor == 1:
            if 470 <= self.y <= 525 and 485 <= self.x <= 745: allowed = True  # 상단 복도
            if 525 <= self.y <= 645 and 485 <= self.x <= 600: allowed = True  # 상단 좌측 복도
            if 525 <= self.y <= 645 and 655 <= self.x <= 745: allowed = True  # 계단
            elif 330 <= self.y <= 470 and 20 <= self.x <= 485: allowed = True  # 좌측 복도
            elif 330 <= self.y <= 470 and 745 <= self.x <= 1210: allowed = True  # 우측 복도
            elif 50 <= self.y <= 330 and 535 <= self.x <= 695: allowed = True  # 하단 복도
            elif 330 <= self.y <= 470 and 485 <= self.x <= 745: allowed = True  # 중앙 복도
        elif play_mode.background.floor == 2:
            if 470 <= self.y <= 500 and 490 <= self.x <= 755: allowed = True  # 상단 복도
            elif 500 <= self.y <= 645 and 490 <= self.x <= 590: allowed = True  # 계단
            elif 330 <= self.y <= 470 and 20 <= self.x <= 1210: allowed = True  # 중앙 복도

        # 허용영역이 아니라면 → 이전 위치로 복귀
        if not allowed:
            self.x, self.y = self.prev_x, self.prev_y

    def on_stairs(self):
        if play_mode.background.floor == 1:
            if (play_mode.background.stair_1_x1 <= self.x <= play_mode.background.stair_1_x2 and
                play_mode.background.stair_1_y1 <= self.y <= play_mode.background.stair_1_y2):
                self.he_is = 1
                return 1
        elif play_mode.background.floor == 2:
            if (play_mode.background.stair_2_x1 <= self.x <= play_mode.background.stair_2_x2 and
                play_mode.background.stair_2_y1 <= self.y <= play_mode.background.stair_2_y2):
                self.he_is = 1
                return 1

        self.he_is = 0
        return 0

    def enter_room(self):
        self.enter_door = 0

        if play_mode.background.floor == 1:
            if 450 <= self.y <= 470:
                if 90 <= self.x <= 185:
                    self.enter_door = 1
                    return 1
                if 265 <= self.x <= 360:
                    self.enter_door = 2
                    return 2
                if 875 <= self.x <= 965:
                    self.enter_door = 3
                    return 3
                if 1045 <= self.x <= 1140:
                    self.enter_door = 4
                    return 4
        elif play_mode.background.floor == 2:
            if 450 <= self.y <= 470:
                if 90 <= self.x <= 185:
                    self.enter_door = 5
                    return 5
                if 265 <= self.x <= 360:
                    self.enter_door = 6
                    return 6
                if 885 <= self.x <= 970:
                    self.enter_door = 7
                    return 7
                if 1055 <= self.x <= 1145:
                    self.enter_door = 8
                    return 8
        return 0

    def exit_lab(self):
        self.lab_exit = 0

        # 1층 연구실 (Lab 11, 12, 13, 14)의 출구 범위
        if 11 <= self.lab <= 14:
            # 535 <= x <= 720 (X축) 및 0 <= y <= 40 (Y축)
            if 535 <= self.x <= 720 and 0 <= self.y <= 80:
                self.lab_exit = 1
                return 1

        # 2층 연구실 (Lab 21, 22, 23, 24)의 출구 범위
        elif 21 <= self.lab <= 24:
            # 535 <= x <= 730 (X축) 및 0 <= y <= 40 (Y축) (draw 함수 기준)
            if 535 <= self.x <= 730 and 0 <= self.y <= 80:
                self.lab_exit = 1
                return 1

    def exit_main_door(self):
        self.main_door = 0

        if play_mode.background.floor == 1:
            if 570 <= self.x <= 665 and 20 <= self.y <= 160:
                self.main_door = 1
                return 1


    def handle_event(self, event):
        # FlashLight Toggle ON/OFF
        if event.type == SDL_KEYDOWN and event.key == SDLK_e:
            self.flashlight ^= 1
            return

        # 계단 1층 <-> 2층
        if self.he_is == 1:
            if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
                if play_mode.background.floor == 1:
                    play_mode.background.floor = 2
                    play_mode.background.load_image()
                    self.x, self.y = play_mode.background.start_pos_floor_2
                    self.enter_door = 0
                elif play_mode.background.floor == 2:
                    play_mode.background.floor = 1
                    play_mode.background.load_image()
                    self.x, self.y = play_mode.background.start_pos_floor_1
                    self.enter_door = 0
                return

        # 정문
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return

        # 연구실
        if event.type == SDL_KEYDOWN and event.key == SDLK_f:
            if self.lab == 0:  # lab 밖에서만 들어감
                if self.enter_door == 1 and play_mode.background.floor == 1:
                    self.lab = 11
                    self.last_entered_door = 1
                    play_mode.background.load_image()
                    self.x, self.y = play_mode.background.start_pos_lab
                    return
                elif self.enter_door == 2 and play_mode.background.floor == 1:
                    self.lab = 12
                    self.last_entered_door = 2
                    play_mode.background.load_image()
                    self.x, self.y = play_mode.background.start_pos_lab
                    return
                elif self.enter_door == 3 and play_mode.background.floor == 1:
                    self.lab = 13
                    self.last_entered_door = 3
                    play_mode.background.load_image()
                    self.x, self.y = play_mode.background.start_pos_lab
                    return
                elif self.enter_door == 4 and play_mode.background.floor == 1:
                    self.lab = 14
                    self.last_entered_door = 4
                    play_mode.background.load_image()
                    self.x, self.y = play_mode.background.start_pos_lab
                    return
                elif self.enter_door == 5 and play_mode.background.floor == 2:
                    self.lab = 21
                    self.last_entered_door = 5
                    play_mode.background.load_image()
                    self.x, self.y = play_mode.background.start_pos_lab
                    return
                elif self.enter_door == 6 and play_mode.background.floor == 2:
                    self.lab = 22
                    self.last_entered_door = 6
                    play_mode.background.load_image()
                    self.x, self.y = play_mode.background.start_pos_lab
                    return
                elif self.enter_door == 7 and play_mode.background.floor == 2:
                    self.lab = 23
                    self.last_entered_door = 7
                    play_mode.background.load_image()
                    self.x, self.y = play_mode.background.start_pos_lab
                    return
                elif self.enter_door == 8 and play_mode.background.floor == 2:
                    self.lab = 24
                    self.last_entered_door = 8
                    play_mode.background.load_image()
                    self.x, self.y = play_mode.background.start_pos_lab
                    return

        # 연구실 나가기 (출구 범위에서만 f로 나감)
        if self.lab != 0 and self.lab_exit == 1 and event.type == SDL_KEYDOWN and event.key == SDLK_f:
            self.lab = 0
            play_mode.background.load_image()
            if self.last_entered_door == 1: self.x, self.y = 137, 460
            if self.last_entered_door == 2: self.x, self.y = 320, 460
            if self.last_entered_door == 3: self.x, self.y = 920, 460
            if self.last_entered_door == 4: self.x, self.y = 1095, 460

            if self.last_entered_door == 5: self.x, self.y = 137, 460
            if self.last_entered_door == 6: self.x, self.y = 320, 460
            if self.last_entered_door == 7: self.x, self.y = 920, 460
            if self.last_entered_door == 8: self.x, self.y = 1095, 460



        if event.key in (SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN):
            cur_xdir, cur_ydir = self.x_dir, self.y_dir
            if event.type == SDL_KEYDOWN:
                if event.key == SDLK_LEFT:self.x_dir -= 1
                elif event.key == SDLK_RIGHT:self.x_dir += 1
                elif event.key == SDLK_UP:self.y_dir += 1
                elif event.key == SDLK_DOWN:self.y_dir -= 1
            elif event.type == SDL_KEYUP:
                if event.key == SDLK_LEFT:self.x_dir += 1
                elif event.key == SDLK_RIGHT:self.x_dir -= 1
                elif event.key == SDLK_UP:self.y_dir -= 1
                elif event.key == SDLK_DOWN:self.y_dir += 1

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
        self.prev_x, self.prev_y = self.x, self.y
        self.state_machine.update()
        import play_mode
        self.handle_collision()
        self.on_stairs()
        self.enter_room()
        self.exit_main_door()
        self.exit_lab()

    def draw(self):
        self.state_machine.draw()
        self.font.draw(self.x - 60, self.y + 50, f'({self.x:.1f}, {self.y:.1f})', (255, 255, 0))
        draw_rectangle(*self.get_bb())


        # 계단 사각형 테두리 그리기
        if self.lab == 0:
            if play_mode.background.floor == 1:
                draw_rectangle(play_mode.background.stair_1_x1,
                               play_mode.background.stair_1_y1,
                               play_mode.background.stair_1_x2,
                               play_mode.background.stair_1_y2)
            elif play_mode.background.floor == 2:
                draw_rectangle(play_mode.background.stair_2_x1,
                               play_mode.background.stair_2_y1,
                               play_mode.background.stair_2_x2,
                               play_mode.background.stair_2_y2)

            if self.he_is == 1:
                if play_mode.background.floor == 1:
                    self.font.draw(600, 580, 'Press SPACE to go UP', (255, 255, 0))
                if play_mode.background.floor == 2:
                    self.font.draw(420, 580, 'Press SPACE to go DOWN', (255, 255, 0))

            # 문 enter 테두리
            if play_mode.background.floor == 1:
                draw_rectangle(90, 450, 185, 470)
                draw_rectangle(265, 450, 360, 470)
                draw_rectangle(875, 450, 965, 470)
                draw_rectangle(1045, 450, 1140, 470)
                if self.enter_door == 1:self.font.draw(60, 500, 'Press f to enter', (255, 255, 0))
                elif self.enter_door == 2:self.font.draw(235, 500, 'Press f to enter', (255, 255, 0))
                elif self.enter_door == 3:self.font.draw(840, 500, 'Press f to enter', (255, 255, 0))
                elif self.enter_door == 4:self.font.draw(1010, 500, 'Press f to enter', (255, 255, 0))
            elif play_mode.background.floor == 2:
                draw_rectangle(90, 450, 185, 470)
                draw_rectangle(265, 450, 360, 470)
                draw_rectangle(885, 450, 970, 470)
                draw_rectangle(1055, 450, 1145, 470)
                if self.enter_door == 5: self.font.draw(60, 500, 'Press f to enter', (255, 255, 0))
                elif self.enter_door == 6:self.font.draw(235, 500, 'Press f to enter', (255, 255, 0))
                elif self.enter_door == 7:self.font.draw(845, 500, 'Press f to enter', (255, 255, 0))
                elif self.enter_door == 8:self.font.draw(1015, 500, 'Press f to enter', (255, 255, 0))

            # 정문 테두리
            if play_mode.background.floor == 1:
                draw_rectangle(570, 20, 665, 160)
                if self.main_door == 1:
                    self.font.draw(540, 140, 'Press ESC to exit', (0, 255, 0))

        else:
            # 연구실 테두리
            if self.lab_exit == 1: self.font.draw(550, 20, 'Press f to exit', (255, 255, 0))

            if 11 <= self.lab <= 14:
                draw_rectangle(535, 0, 720, 80)
                draw_rectangle(305, 80, 975, 500)
            if 21 <= self.lab <= 24:
                draw_rectangle(535, 0, 730, 80)
                draw_rectangle(285, 40, 1000, 500)

        '''
        if self.flashlight == 1:
            self.image2.draw(self.x - 5, self.y + 35)
        elif self.flashlight == 0:
            self.image3.draw(self.x, self.y + 25)
        '''
