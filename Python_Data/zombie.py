from pico2d import *

import random
import math
import game_framework
import game_world
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector
import common


# zombie Run Speed
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 5.0  # Km / Hour
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

        self.loc_no = 0

        self.last_lab = 0


    def get_bb(self):
        return self.x - 50, self.y - 50, self.x + 50, self.y + 50


    def update(self):
        if self.state == 'Walk':
            self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8.0

        import common

        # reporter 존재하면 lab 변경 시만 위치 스폰
        if common.reporter is not None:
            if common.reporter.lab != self.last_lab and common.reporter.lab != 0:
                if 11 <= common.reporter.lab <= 14:
                    self.x = random.randint(350, 900)
                    self.y = random.randint(200, 400)
                elif 21 <= common.reporter.lab <= 24:
                    self.x = random.randint(350, 900)
                    self.y = random.randint(200, 400)
                self.last_lab = common.reporter.lab

            if common.reporter.lab != 0: self.bt.run()
            else: self.state = 'Idle'

        self.bt.run()


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

        if common.reporter.lab != 0:
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
        if not x or not y:
            raise ValueError('목적위치가 설정되어야 합니다.')
        self.tx, self.ty = x, y
        return BehaviorTree.SUCCESS # 목적지 설정 성공


    # 거리 비교 함수
    def distance_less_than(self, x1, y1, x2, y2, r):  # r은 미터 단위
        distance2 = (x1 - x2) ** 2 + (y1 - y2) ** 2
        return distance2 < (PIXEL_PER_METER * r) ** 2


    def move_little_to(self, tx, ty):
        self.dir = math.atan2(ty - self.y, tx - self.x)
        distance = RUN_SPEED_PPS * game_framework.frame_time
        self.x += distance * math.cos(self.dir)
        self.y += distance * math.sin(self.dir)


    def move_to(self, r=0.5):
        self.state = 'Walk'
        self.move_little_to(common.reporter.x, common.reporter.y)
        if self.distance_less_than(common.reporter.x, common.reporter.y, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING


    def set_random_location(self):
        # 여기를 채우시오.
        self.tx, self.ty = random.randint(100, 1180), random.randint(100, 924)
        return BehaviorTree.SUCCESS


    def if_reporter_nearby(self, r):
        if self.distance_less_than(common.reporter.x, common.reporter.y, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL


    def move_to_reporter(self, r=0.5):
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
        '''
        # wander
        wander_action = Action('랜덤 위치 설정', self.set_random_location)
        wander_move = Action('랜덤 이동', self.move_to, 0.5)
        wander = Sequence('배회', wander_action, wander_move)

        # chase
        chase_move = Action('추적 이동', self.move_to_reporter)

        # 🔥 핵심: Condition을 Selector와 연결
        root = Selector('root',
                        Sequence('추격 시퀀스',
                                 Condition('근접?', self.if_reporter_nearby, 5),
                                 chase_move
                                 ),
                        wander
                        )

        self.bt = BehaviorTree(root)
        '''
        a1 = Action('Set target location', self.set_target_location, 500, 50)
        a2 = Action('Move to', self.move_to)
        root = move_to_target_location = Sequence('Move to target location', a1, a2)
        a3 = Action('Set random location', self.set_random_location)
        root = wander = Sequence('Wander', a3, a2)
        c1 = Condition('소년이 근처에 있는가?', self.if_reporter_nearby, 5)
        a4 = Action('소년한테 접근', self.move_to_reporter)
        root = chase_boy = Sequence('소년을 추적', c1, a4)
        self.bt = BehaviorTree(root)



