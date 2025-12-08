from pico2d import *

import random
import math
import game_framework
import game_world
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector
import common


# zombie Run Speed
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 10.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# zombie Action Speed
TIME_PER_ACTION = 1.0
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8.0

animation_names = ['Walk', 'Idle']


class Zombie:
    image = None
    font = None
    marker_image = None

    def load_images(self):
        if Zombie.image == None:
            Zombie.image = load_image('Zombie_Sheet.png')
            Zombie.font = load_font('ENCR10B.TTF', 40)


    def __init__(self, x=None, y=None):
        self.x = x if x else random.randint(500, 700)
        self.y = y if y else random.randint(500, 700)
        self.load_images()
        self.dir = 0.0      # radian 값으로 방향을 표시
        self.speed = 0.0
        self.frame = random.randint(0, 7)
        self.state = 'Idle'
        self.ball_count = 0

        self.last_dir = 1.0

        self.tx, self.ty = 600, 600
        # 여기를 채우시오.

        self.build_behavior_tree()

        self.patrol_locations = [(43, 274), (1118,274),(1050,494),(575, 804),(235, 991),
                                 (575, 804),(1050, 494),(1118, 274)]
        self.loc_no = 0

        self.last_lab = 0


    def get_bb(self):
        return self.x - 50, self.y - 50, self.x + 50, self.y + 50


    def update(self):
        if self.state == 'Walk':
            self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8.0
        # fill here


        import common

        if not hasattr(common.reporter, 'lab') or common.reporter.lab is None: return

        if common.reporter.lab != self.last_lab and common.reporter.lab != 0:
            # 연구실 내부 영역에 맞게 랜덤 위치 설정
            if 11 <= common.reporter.lab <= 14:
                # 1층: x 305~975, y 80~500 (안전하게 내부 중앙)
                self.x = random.randint(350, 950)
                self.y = random.randint(550, 850)
            elif 21 <= common.reporter.lab <= 24:
                # 2층: x 285~1000, y 40~500
                self.x = random.randint(350, 950)
                self.y = random.randint(850, 1100)
            self.last_lab = common.reporter.lab

        self.bt.run()  # 매 프레임마다 행동트리를 root 부터 시작해서 실행함.


    def draw(self):
        '''
        import common
        if common.reporter is None: return
        if common.reporter.lab == 0: return


        lab = common.reporter.lab
        in_lab = False

        # 1층 연구실 내부 영역 체크
        if 11 <= lab <= 14:
            if 305 <= self.x <= 975 and 80 <= self.y <= 500:
                in_lab = True

        # 2층 연구실 영역
        elif 21 <= lab <= 24:
            if 285 <= self.x <= 1000 and 40 <= self.y <= 500:
                in_lab = True

        if not in_lab:
            return
        '''

        if self.state == 'Walk':
            frame_index = int(self.frame)
            current_direction = self.dir
            flip = 'h' if math.cos(current_direction) < 0 else None
        else:
            frame_index = 0
            current_direction = self.last_dir
            flip = None

        sx = frame_index * 150
        sy = 0

        if flip == 'h':
            Zombie.image.clip_composite_draw(sx, sy, 139, 200, 0, 'h', self.x, self.y, 70, 100)
        else:
            Zombie.image.clip_draw(sx, sy, 139, 200, self.x, self.y, 70, 100)

        draw_rectangle(*self.get_bb())
        draw_circle(self.x, self.y, int(5.0 * PIXEL_PER_METER), 255, 255, 255)

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        pass


    def set_target_location(self, x=None, y=None):
        # 여기를 채우시오.
        if not x or not y:
            raise ValueError('목적위치가 설정되어야 합니다.')
        self.tx, self.ty = x, y
        return BehaviorTree.SUCCESS # 목적지 설정 성공
        pass


    # 거리 비교 함수
    def distance_less_than(self, x1, y1, x2, y2, r):  # r은 미터 단위
        # 여기를 채우시오.
        distance2 = (x1-x2)**2 + (y1-y2)**2
        return distance2 < (PIXEL_PER_METER * r) ** 2
        pass



    def move_little_to(self, tx, ty):
        # 여기를 채우시오.
        distance = RUN_SPEED_PPS * game_framework.frame_time

        new_dir = math.atan2(ty - self.y, tx - self.x)

        if self.state == 'Walk':
            self.dir = new_dir
            self.last_dir = self.dir

        self.x += distance * math.cos(self.dir)
        self.y += distance * math.sin(self.dir)
        pass



    def move_to(self, r=0.5):
        self.state = 'Walk'
        self.move_little_to(self.tx, self.ty)

        if self.distance_less_than(self.tx, self.ty, self.x, self.y, r):
            self.state = 'Idle'
            return BehaviorTree.SUCCESS

        return BehaviorTree.RUNNING



    def set_random_location(self):
        # 여기를 채우시오.
        self.tx, self.ty = random.randint(100, 1180), random.randint(100, 924)
        return BehaviorTree.SUCCESS
        pass


    def if_boy_nearby(self, distance):
        import common
        if common.reporter is None:
            return BehaviorTree.FAIL

        dx = self.x - common.reporter.x
        dy = self.y - common.reporter.y
        dist = math.sqrt(dx * dx + dy * dy)

        # trigger distance
        if dist < distance * PIXEL_PER_METER:
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL





    def move_to_boy(self, r=0.5):
        import common

        dx = common.reporter.x - self.x
        dy = common.reporter.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        self.state = 'Walk'
        self.dir = math.atan2(dy, dx)

        step = RUN_SPEED_PPS * game_framework.frame_time
        self.x += step * math.cos(self.dir)
        self.y += step * math.sin(self.dir)

        # 도착 판정
        if dist < PIXEL_PER_METER * r:
            self.state = 'Idle'
            return BehaviorTree.SUCCESS

        return BehaviorTree.RUNNING


    def get_patrol_location(self):
        # 여기를 채우시오.
        self.tx, self.ty = self.patrol_locations[self.loc_no]
        self.loc_no = (self.loc_no + 1) % len(self.patrol_locations)
        return BehaviorTree.SUCCESS
        pass


    def build_behavior_tree(self):
        # 배회 설정
        wander_action = Action('랜덤 위치 설정', self.set_random_location)
        wander_move = Action('랜덤 이동', self.move_to, 0.5)
        wander = Sequence('배회', wander_action, wander_move)

        # 추격 트리거
        chase_trigger = Condition('추격 트리거', self.if_boy_nearby, 5)

        # 추격 이동
        chase_move = Action('추격 이동', self.move_to_boy)

        # chase는 trigger → move만
        chase = Sequence('추격', chase_trigger, chase_move)

        # root: chase > wander fallback
        self.bt = BehaviorTree(Selector('root', chase, wander))



