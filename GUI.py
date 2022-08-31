from GameMap import *

class Checkbox:
    def __init__(self, surface, x, y, color=(230, 230, 230), caption="", outline_color=(0, 0, 0),
                 check_color=(0, 0, 0), font_size=22, font_color=(0, 0, 0), text_offset=(28, 1)):
        self.surface = surface
        self.x = x
        self.y = y
        self.color = color
        self.caption = caption
        self.oc = outline_color
        self.cc = check_color
        self.fs = font_size
        self.fc = font_color
        self.to = text_offset
        # checkbox object
        self.checkbox_obj = pygame.Rect(self.x, self.y, 12, 12)
        self.checkbox_outline = self.checkbox_obj.copy()
        # variables to test the different states of the checkbox
        self.checked = False
        self.active = True

    def _draw_button_text(self):
        self.font = pygame.font.SysFont("SimHei", self.fs)
        self.font_surf = self.font.render(self.caption, True, self.fc)
        w, h = self.font.size(self.caption)
        self.font_pos = (self.x + 110 / 2 - w / 2 + self.to[0], self.y + 12 / 2 - h / 2 + self.to[1])
        self.surface.blit(self.font_surf, self.font_pos)

    def render_checkbox(self):
        if self.checked:
            pygame.draw.rect(self.surface, self.color, self.checkbox_obj)
            pygame.draw.rect(self.surface, self.oc, self.checkbox_outline, 1)
            pygame.draw.circle(self.surface, self.cc, (self.x + 6, self.y + 6), 4)
        else:
            pygame.draw.rect(self.surface, self.color, self.checkbox_obj)
            pygame.draw.rect(self.surface, self.oc, self.checkbox_outline, 1)
        self._draw_button_text()

    def updateState(self, state):
        self.active = state

    def click_checkbox(self, x, y):
        if self.active:
            px, py, w, h = self.checkbox_obj
            if px < x < px + w and py < y < py + h:
                if self.checked:
                    self.checked = False
                else:
                    self.checked = True
                self.render_checkbox()

    def is_checked(self):
        if self.checked is True:
            return True
        else:
            return False

    def is_unchecked(self):
        if self.checked is False:
            return True
        else:
            return False

class Button:
    def __init__(self, screen, text, x, y, color, enable):
        self.screen = screen
        self.width = BUTTON_WIDTH
        self.height = BUTTON_HEIGHT
        self.button_color = color
        self.text_color = (255, 255, 255)
        # 判断是哪个按钮
        self.enable = enable
        # 设置字体
        self.font = pygame.font.SysFont("SimHei", BUTTON_HEIGHT * 2 // 3)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        # 将按钮的左上角对其x,y点
        self.rect.topleft = (x, y)
        self.text = text
        self.init_msg()

    # 区分按钮是否被点击过,用不同颜色区分
    def init_msg(self):
        if self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
        else:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    # 画出按钮
    def draw(self):
        if self.enable:
            self.screen.fill(self.button_color[0], self.rect)
        else:
            self.screen.fill(self.button_color[1], self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)


# 开始按钮
class StartButton(Button):
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [(26, 173, 25), (158, 217, 157)], True)

    # 开始游戏方法
    def click(self, game):
        if self.enable:
            game.start()
            game.winner = None
            game.balanceInfo = None
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            game.player = MAP_ENTRY_TYPE.MAP_PLAYER_ONE
            game.selects1.updateState(False)
            game.selects2.updateState(False)
            game.selects3.updateState(False)
            if game.selects1.checked:
                game.AI.isIntelligence = True
            else:
                game.AI.isIntelligence = False
            if game.selects2.checked:
                game.AI.isBalance = True
            else:
                game.AI.isBalance = False
            if game.selects3.checked:
                game.AI.isFirst = False
                game.AI.chessType = MAP_ENTRY_TYPE.MAP_PLAYER_TWO
                game.useAI = False
            else:
                game.AI.chessType = MAP_ENTRY_TYPE.MAP_PLAYER_ONE
                game.useAI = True
            return True
        return False

    # 取消点击状态
    def unclick(self,game):
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True
            game.selects1.updateState(True)
            game.selects2.updateState(True)
            game.selects3.updateState(True)
            game.AI.isFirstStep=True


# 放弃按钮
class GiveupButton(Button):
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [(230, 67, 64), (236, 139, 137)], False)

    # 放弃游戏方法
    def click(self, game):
        if self.enable:
            # 结束游戏
            game.is_play = False
            # 若未分胜负则将让对手获胜
            if game.winner is None:
                game.winner = game.map.reverseTurn(game.player)
            # 设置点击的按钮状态
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False

    # 取消按钮的点击
    def unclick(self, _):
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True