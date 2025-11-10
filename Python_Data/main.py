'''
1 주차 : 리소스 확보
2 주차 : 게임 화면 세팅
3 주차 : 캐릭터, 맵 구현
4 주차 : 좀비 이동 구현
5 주차 : 스킬 오브젝트 구현 + 스킬의 효과 구현
6 주차 : 승리 조건/판정 구현
7 주차 : 소리 구현
8 주차 : 밸런스 조정
9 주차 : 발표 준비
'''

import game_framework
from pico2d import *
import play_mode as start_mode

open_canvas()
game_framework.run(start_mode)
close_canvas()

