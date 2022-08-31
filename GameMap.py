from enum import IntEnum
import pygame
from pygame.locals import *

GAME_VERSION = 'V1.0'

REC_SIZE = 50
CHESS_RADIUS = REC_SIZE // 2 - 2
CHESS_LEN = 15
MAP_WIDTH = CHESS_LEN * REC_SIZE
MAP_HEIGHT = CHESS_LEN * REC_SIZE

INFO_WIDTH = 200
BUTTON_WIDTH = 140
BUTTON_HEIGHT = 50

SCREEN_WIDTH = MAP_WIDTH + INFO_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT


class MAP_ENTRY_TYPE(IntEnum):
    MAP_EMPTY = 0,
    MAP_PLAYER_ONE = 1,
    MAP_PLAYER_TWO = 2,
    MAP_NONE = 3,  # out of map range


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = [[0 for x in range(self.width)] for y in range(self.height)]
        self.steps = []

    # 重置游戏状态
    def reset(self):
        for y in range(self.height):
            for x in range(self.width):
                self.map[y][x] = 0
        self.steps = []

    # 返回当前玩家的对手
    def reverseTurn(self, turn):
        if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
            return MAP_ENTRY_TYPE.MAP_PLAYER_TWO
        else:
            return MAP_ENTRY_TYPE.MAP_PLAYER_ONE

    # 将map中的x,y映射成实际的位置
    def getMapUnitRect(self, x, y):
        map_x = x * REC_SIZE
        map_y = y * REC_SIZE

        return (map_x, map_y, REC_SIZE, REC_SIZE)

    # 将电机的实际位置映射成map中的位置
    def MapPosToIndex(self, map_x, map_y):
        x = map_x // REC_SIZE
        y = map_y // REC_SIZE
        return (x, y)

    # 判断所点击的位置是否在棋盘上
    def isInMap(self, map_x, map_y):
        if (map_x <= 0 or map_x >= MAP_WIDTH or
                map_y <= 0 or map_y >= MAP_HEIGHT):
            return False
        return True

    # 判断棋盘中x,y处是否为空
    def isEmpty(self, x, y):
        return (self.map[y][x] == 0)

    # 落子操作,更新map的值,以及将此步数添加进steps
    def click(self, x, y, type):
        self.map[y][x] = type.value
        self.steps.append((x, y))

    # 画棋盘上的棋子
    def drawChess(self, screen):
        # 设置玩家棋子颜色
        # (88, 87, 86)
        player_one = (45, 45, 45)
        # (255, 251, 240)
        player_two = (255, 255, 255)
        player_color = [player_one, player_two]
        # 设置棋子上表示步数数字的字体
        font = pygame.font.SysFont(None, REC_SIZE * 2 // 3)
        black = pygame.image.load(r"resource/black.png")
        white = pygame.image.load(r"resource/white.png")
        radius = CHESS_RADIUS
        black = pygame.transform.smoothscale(black, (radius * 2, radius * 2))
        white = pygame.transform.smoothscale(white, (radius * 2, radius * 2))
        player_chess = [black, white]
        # 画出棋盘上的棋子
        for i in range(len(self.steps)):
            x, y = self.steps[i]
            map_x, map_y, width, height = self.getMapUnitRect(x, y)
            # radius = CHESS_RADIUS
            pos = (map_x + width // 2, map_y + height // 2)
            pos_x,pos_y= map_x + width // 2, map_y + height // 2
            turn = self.map[y][x]
            if turn == 1:
                op_turn = 2
            else:
                op_turn = 1
            # 填充棋盘窗口颜色
            # pygame.draw.rect(self.screen, light_yellow, pygame.Rect(0, 0, MAP_WIDTH, SCREEN_HEIGHT)
            # self.screen.blit(background,(0,0),pygame.Rect(0, 0, MAP_WIDTH, SCREEN_HEIGHT))
            screen.blit(player_chess[turn - 1], (pos_x-radius, pos_y-radius))
            # pygame.draw.circle(screen, player_color[turn - 1], pos, radius)
            # 画棋子上的数字
            # , player_color[turn - 1]
            msg_image = font.render(str(i), True, player_color[op_turn - 1])
            msg_image_rect = msg_image.get_rect()
            msg_image_rect.center = pos
            screen.blit(msg_image, msg_image_rect)
        # 标示出最后落子的位置
        if len(self.steps) > 0:
            last_pos = self.steps[-1]
            map_x, map_y, width, height = self.getMapUnitRect(last_pos[0], last_pos[1])
            purple_color = (255, 0, 255)
            point_list = [(map_x, map_y), (map_x + width, map_y),
                          (map_x + width, map_y + height), (map_x, map_y + height)]
            pygame.draw.lines(screen, purple_color, True, point_list, 2)

    # 画棋盘
    def drawBackground(self, screen):
        # 棋盘线颜色(0, 0, 0)
        color = (0, 0, 0)
        for y in range(self.height):
            # 画横线
            start_pos, end_pos = (REC_SIZE // 2, REC_SIZE // 2 + REC_SIZE * y), (
                MAP_WIDTH - REC_SIZE // 2, REC_SIZE // 2 + REC_SIZE * y)
            # 棋盘中间的先加粗
            if y == self.height // 2:
                width = 3
            else:
                width = 2
            pygame.draw.line(screen, color, start_pos, end_pos, width)

        for x in range(self.width):
            # 画竖线
            start_pos, end_pos = (REC_SIZE // 2 + REC_SIZE * x, REC_SIZE // 2), (
                REC_SIZE // 2 + REC_SIZE * x, MAP_HEIGHT - REC_SIZE // 2)
            # 棋盘中间的先加粗
            if x == self.width // 2:
                width = 2
            else:
                width = 1
            pygame.draw.line(screen, color, start_pos, end_pos, width)
        # 画星位和天元
        rec_size = 8
        pos = [(3, 3), (11, 3), (3, 11), (11, 11), (7, 7)]
        for (x, y) in pos:
            pygame.draw.circle(screen, color, (REC_SIZE // 2 + x * REC_SIZE - rec_size // 2 + 4, REC_SIZE // 2 + y * REC_SIZE - rec_size // 2 + 4), rec_size - 3)
    # 判断棋盘是否被填满
    def is_map_filld(self):
        for i in range(len(self.map)):
            for j in range(len(self.map)):
                if self.map[i][j] == 0:
                    return False
        return True
