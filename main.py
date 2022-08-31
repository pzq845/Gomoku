import pygame
from pygame.locals import *
from GameMap import *
from ChessAI import *
from GUI import *
# 按钮类
from rule import Breaker_InfoDir


class Game():
    def __init__(self, caption):
        # 设置两个选择框
        self.selects1 = None
        self.selects2 = None
        self.selects3 = None
        pygame.init()
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        # 设置游戏窗口标题
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        # 将按钮添加到游戏中
        self.buttons = []
        self.buttons.append(StartButton(self.screen, '开始', MAP_WIDTH + 30, 15))
        self.buttons.append(GiveupButton(self.screen, '放弃', MAP_WIDTH + 30, BUTTON_HEIGHT + 45))
        # 设置选择框属性
        self.selects1 = Checkbox(self.screen, MAP_WIDTH + 30, BUTTON_HEIGHT + 150, caption="是否使用AI")
        self.selects2 = Checkbox(self.screen, MAP_WIDTH + 30, BUTTON_HEIGHT + 200, caption="启用禁手规则")
        self.selects3 = Checkbox(self.screen, MAP_WIDTH + 30, BUTTON_HEIGHT + 250, caption="先手")
        # 游戏状态设置为否
        self.is_play = False
        # 创建游戏棋盘
        self.map = Map(CHESS_LEN, CHESS_LEN)
        # 设置游戏玩家的棋子
        self.player = MAP_ENTRY_TYPE.MAP_PLAYER_ONE
        self.action = None
        # 设置AI
        self.AI = ChessAI(CHESS_LEN, False, False, True, MAP_ENTRY_TYPE.MAP_PLAYER_ONE)
        # 判断是否由AI下棋
        self.useAI = False
        self.winner = None
        # 若游戏因禁手违规结束记录禁手类型
        self.balanceInfo = None
        self.dorpChessSound = pygame.mixer.Sound("resource/dorpChessSound.wav")
        self.dorpChessSound.set_volume(0.2)

    # 游戏开始
    def start(self):
        # 将游戏状态设置为开始
        self.is_play = True
        # 重置棋局状态
        self.map.reset()

    # 游戏开始
    def play(self):
        # 记录上一帧到现在的时间
        self.clock.tick(60)
        # 棋盘背景颜色
        light_yellow = (0xE3, 0x92, 0x65)
        background = pygame.image.load(r"resource/img.png")
        # 填充棋盘窗口颜色
        # pygame.draw.rect(self.screen, light_yellow, pygame.Rect(0, 0, MAP_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(background,(0,0),pygame.Rect(0, 0, MAP_WIDTH, SCREEN_HEIGHT))
        # 填充右侧按钮窗口颜色
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(MAP_WIDTH, 0, INFO_WIDTH, SCREEN_HEIGHT))

        # 画按钮
        for button in self.buttons:
            button.draw()
        # 画选择框
        self.selects1.render_checkbox()
        self.selects2.render_checkbox()
        self.selects3.render_checkbox()
        # 游戏进行中并且未分胜负
        if self.is_play and not self.isOver():
            # 是否由AI下棋
            if self.useAI:
                x, y = self.AI.findBestChess(self.map.map, self.player)
                self.checkClick(x, y, True)
                self.dorpChessSound.play()
                self.useAI = False
            # 是否由玩家操作
            if self.action is not None:
                self.checkClick(self.action[0], self.action[1])
                self.dorpChessSound.play()
                self.action = None
            # 游戏若未结束则将鼠标高亮显示
            if not self.isOver():
                self.changeMouseShow()

        # 若分胜负则显示赢家
        if self.isOver():
            self.showWinner()
        # 画背景
        self.map.drawBackground(self.screen)
        # 画棋子
        self.map.drawChess(self.screen)

    # 画出鼠标移动时的红圈,以便显示
    def changeMouseShow(self):
        # 得到鼠标位置
        map_x, map_y = pygame.mouse.get_pos()
        x, y = self.map.MapPosToIndex(map_x, map_y)
        # 若鼠标所指向的位置是在棋盘内并且此处未落子,则隐藏鼠标指针而是将鼠标指向处用红圈标明
        if self.map.isInMap(map_x, map_y) and self.map.isEmpty(x, y):
            pygame.mouse.set_visible(False)
            light_red = (213, 90, 107)
            pos, radius = (map_x, map_y), CHESS_RADIUS
            pygame.draw.circle(self.screen, light_red, pos, radius)
        else:
            pygame.mouse.set_visible(True)

    # 判断按下位置
    def checkClick(self, x, y, isAI=False):
        # 将当前玩家的棋子下在指定位置
        self.map.click(x, y, self.player)
        # 判断游戏是否启用禁手规则
        if self.selects2.checked:
            # 若此时先行的为玩家(先手)
            if self.player == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
                # 记录当前落子的位置是否为禁手
                breaker_type = ChessAI.isBalanceBreaker(self.AI, self.map.map, x, y)
                if breaker_type == Balance_Breaker_Type.NONE:
                    pass
                # 若为禁手则游戏分胜负显示相关信息,并且将禁手类型记录
                else:
                    self.balanceInfo = breaker_type
                    self.winner = MAP_ENTRY_TYPE.MAP_PLAYER_TWO
                    self.click_button(self.buttons[1])
                    return
        # 判断是否游戏结束
        # isAlreadyWin(self, board, x, y, mine, op)
        # if self.AI.isWin(self.map.map, self.player):
        if self.AI.isAlreadyWin(self.map.map, x, y, self.player, self.map.reverseTurn(self.player)):
            # 若游戏分胜负则认为当前的玩家是赢家,并修改按钮状态
            self.winner = self.player
            self.click_button(self.buttons[1])
        # 否则交换下棋方
        elif self.map.is_map_filld():
            self.winner = 3
            self.click_button(self.buttons[1])
        else:
            self.player = self.map.reverseTurn(self.player)
            if not isAI:
                self.useAI = True

    # 鼠标点击操作
    def mouseClick(self, map_x, map_y):
        # 若游戏开始并且未分胜负,且所点击位置在棋盘上、棋盘当前位置为空则记录进action中
        if self.is_play and self.map.isInMap(map_x, map_y) and not self.isOver():
            x, y = self.map.MapPosToIndex(map_x, map_y)
            if self.map.isEmpty(x, y):
                self.action = (x, y)

    # 判断游戏是否结束
    def isOver(self):
        return self.winner is not None

    # 在右下角显示游戏的获胜者
    def showWinner(self):
        def showFont(screen, text, location_x, locaiton_y, height):
            font = pygame.font.SysFont("SimHei", height)
            font_image = font.render(text, True, (0, 0, 255), (255, 255, 255))
            font_image_rect = font_image.get_rect()
            font_image_rect.x = location_x
            font_image_rect.y = locaiton_y
            screen.blit(font_image, font_image_rect)

        # 判断赢家
        if self.winner == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
            str1 = '黑子胜'
        elif self.winner == MAP_ENTRY_TYPE.MAP_PLAYER_TWO:
            str1 = '白子胜'
        else:
            str1 = '平局'
        if self.balanceInfo is not None and self.balanceInfo != Balance_Breaker_Type.NONE:
            showFont(self.screen, Breaker_InfoDir.get(self.balanceInfo), MAP_WIDTH + 25, SCREEN_HEIGHT - 90, 30)
        showFont(self.screen, str1, MAP_WIDTH + 25, SCREEN_HEIGHT - 60, 30)
        pygame.mouse.set_visible(True)

    # 按钮点击操作
    def click_button(self, button):
        if button.click(self):
            # 点击后将另一按钮设置为未点击状态
            for tmp in self.buttons:
                if tmp != button:
                    tmp.unclick(self)

    def check_buttons(self, mouse_x, mouse_y):
        for button in self.buttons:
            if button.rect.collidepoint(mouse_x, mouse_y):
                self.click_button(button)
                break

    def check_select1(self, mouse_x, mouse_y):
        self.selects1.click_checkbox(mouse_x, mouse_y)

    def check_select2(self, mouse_x, mouse_y):
        self.selects2.click_checkbox(mouse_x, mouse_y)

    def check_select3(self, mouse_x, mouse_y):
        self.selects3.click_checkbox(mouse_x, mouse_y)


game = Game("FIVE CHESS " + GAME_VERSION)
while True:
    game.play()
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            game.mouseClick(mouse_x, mouse_y)
            game.check_buttons(mouse_x, mouse_y)
            game.check_select1(mouse_x, mouse_y)
            game.check_select2(mouse_x, mouse_y)
            game.check_select3(mouse_x, mouse_y)
