'''
1 주차 : 리소스 확보
2 주차 : 게임 화면 세팅
3 주차 : 맵 구현
4 주차 : 캐릭터 구현
5 주차 : 좀비 구현
6 주차 : 스킬 구현
7 주차 : 소리 + 승리 판정 구현
8 주차 : 밸런스 조정
9 주차 : 발표 준비
'''

import game_framework
from pico2d import *
import title_mode as start_mode

open_canvas(1280, 720)
game_framework.run(start_mode)
close_canvas()

