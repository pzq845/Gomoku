from GameMap import *
from enum import IntEnum
from random import randint
import time
# from test6.main import Balance_Breaker_Type
from rule import *

AI_SEARCH_DEPTH = 4
AI_LIMITED_MOVE_NUM = 20

# AI类
class ChessAI:
    def __init__(self, chess_len, isIntelligence, isBalance, isFirst, chessType):
        # 棋型的长度
        self.len = chess_len
        # 存储每个棋子在四个方向上是否有被判定过
        self.record = [[[0, 0, 0, 0] for x in range(chess_len)] for y in range(chess_len)]
        # 记录棋盘局面的棋型个数
        self.count = [[0 for x in range(CHESS_TYPE_NUM)] for i in range(2)]
        # 是否使用剪枝算法
        self.isIntelligence = isIntelligence
        # 是否开启禁手
        self.isBalance = isBalance
        # 是否先手
        self.isFirst = isFirst
        # 棋子类型
        self.chessType = chessType
        # 是否是首棋
        self.isFirstStep = True

    # 重置 record 和 count
    def reset(self):
        for y in range(self.len):
            for x in range(self.len):
                for i in range(4):
                    self.record[y][x][i] = 0

        for i in range(len(self.count)):
            for j in range(len(self.count[0])):
                self.count[i][j] = 0
    # 机器下棋
    def click(self, map, x, y, turn):
        map.click(x, y, turn)

    # 评价一个点的对于双方的评分
    def evaluatePointScore(self, board, x, y, mine, opponent):
        dir_offset = [(1, 0), (0, 1), (1, 1), (1, -1)]  # direction from left to right
        for i in range(len(self.count)):
            for j in range(len(self.count[0])):
                self.count[i][j] = 0

        board[y][x] = mine
        self.evaluatePoint(board, x, y, mine, opponent, self.count[mine - 1])
        mine_count = self.count[mine - 1]
        board[y][x] = opponent
        self.evaluatePoint(board, x, y, opponent, mine, self.count[opponent - 1])
        opponent_count = self.count[opponent - 1]
        board[y][x] = 0

        mscore = self.getPointScore(mine_count)
        oscore = self.getPointScore(opponent_count)

        return mscore, oscore

    # 判断x,y在radius范围内有没有其他子
    def hasNeighbor(self, board, x, y, radius):
        start_x, end_x = (x - radius), (x + radius)
        start_y, end_y = (y - radius), (y + radius)

        for i in range(start_y, end_y + 1):
            for j in range(start_x, end_x + 1):
                if i >= 0 and i < self.len and j >= 0 and j < self.len:
                    if board[i][j] != 0:
                        return True
        return False

    # 启发式搜索生成合适的节点来进行搜索
    def genmove(self, board, turn):
        fives = []
        mfours, ofours = [], []
        msfours, osfours = [], []
        if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
            mine = 1
            opponent = 2
        else:
            mine = 2
            opponent = 1
        moves = []
        radius = 1
        for y in range(self.len):
            for x in range(self.len):
                # 判断当前节点在radius范围内有没有棋子
                if board[y][x] == 0 and self.hasNeighbor(board, x, y, radius):
                    # 判断当前下棋点的分值
                    mscore, oscore = self.evaluatePointScore(board, x, y, mine, opponent)
                    point = (max(mscore, oscore), x, y)
                    if mscore >= SCORE_FIVE or oscore >= SCORE_FIVE:
                        fives.append(point)
                    elif mscore >= SCORE_FOUR:
                        mfours.append(point)
                    elif oscore >= SCORE_FOUR:
                        ofours.append(point)
                    elif mscore >= SCORE_SFOUR:
                        msfours.append(point)
                    elif oscore >= SCORE_SFOUR:
                        osfours.append(point)
                    moves.append(point)
        # 如果可以连成5子棋型的位置则直接返回这些位置
        if len(fives) > 0: return fives
        # 返回己方可以形成连四的位置
        if len(mfours) > 0: return mfours
        if len(ofours) > 0:
            if len(msfours) == 0:
                return ofours
            else:
                return ofours + msfours

        moves.sort(reverse=True)
        # 限制节点个数
        if self.maxdepth > 2 and len(moves) > AI_LIMITED_MOVE_NUM:
            moves = moves[:AI_LIMITED_MOVE_NUM]
        return moves

    # alphabeta剪枝搜索最优的下棋点
    def __search(self, board, turn, depth, alpha=SCORE_MIN, beta=SCORE_MAX):
        score = 0
        # 判断是否到达底层
        if depth <= 0:
            self.evaluate(board, turn)
            return score
        # 生成合适的下棋点的数组
        moves = self.genmove(board, turn)
        _, x, y = moves[0]
        bestmove = (x, y)
        if len(moves) == 0:
            return score
        if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
            op_turn = MAP_ENTRY_TYPE.MAP_PLAYER_TWO
        else:
            op_turn = MAP_ENTRY_TYPE.MAP_PLAYER_ONE
        # 负值极大法
        for _, x, y in moves:
            board[y][x] = turn
            # 此步棋后是否胜利
            if self.isAlreadyWin(board, x, y, turn, op_turn):
                score = SCORE_MAX
            else:
                score = - self.__search(board, op_turn, depth - 1, -beta, -alpha)
            board[y][x] = 0
            if score > alpha:
                alpha = score
                bestmove = (x, y)
                if alpha >= beta:
                    break
        # 若当前为顶层则设置当前层的最佳落子点为AI此论落子点
        if depth == self.maxdepth and bestmove:
            self.bestmove = bestmove
        return alpha

        # score = 0
        # if depth == 0:
        #     # 判断当前节点对于当前的下棋方的分数
        #     score = self.evaluate(board, turn)
        #     return score
        # moves = self.genmove(board, turn)
        # if len(moves) == 0:
        #     return score
        # _, x, y = moves[len(moves) - 1]
        # bestmove = (x, y)
        # if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
        #     op_turn = MAP_ENTRY_TYPE.MAP_PLAYER_TWO
        # else:
        #     op_turn = MAP_ENTRY_TYPE.MAP_PLAYER_ONE
        # for _, x, y in moves:
        #     board[y][x] = turn
        #     score = - self.__search(board, op_turn, depth - 1, alpha, beta)
        #     board[y][x] = 0
        #     if turn == self.chessType:
        #         if score > alpha:
        #             bestmove = (x, y)
        #             alpha = score
        #         if alpha >= beta:
        #             if depth == self.maxdepth and bestmove:
        #                 self.bestmove = bestmove
        #             return beta
        #     else:
        #         if score < beta:
        #             bestmove = (x, y)
        #             beta = score
        #         if alpha >= beta:
        #             if depth == self.maxdepth and bestmove:
        #                 self.bestmove = bestmove
        #             return alpha
        #
        # if depth == self.maxdepth and bestmove:
        #     self.bestmove = bestmove
        # return alpha

    # 返回在当前turn方的最佳落棋点,depth为搜索深度
    def search(self, board, turn, depth):
        self.maxdepth = depth
        self.bestmove = None
        moves = None
        score = 0
        if self.isFirst and self.isFirstStep:
            print(self.isFirst)
            print(self.isFirstStep)
            self.isFirstStep = False
            moves = (7, 7)
            self.bestmove = moves
        elif self.isIntelligence:
            # 剪枝算法
            score = self.__search(board, turn, depth)
        else:
            # 随机下棋(用于测试一部分功能)
            score = self.__search1(board, turn, depth)
        x, y = self.bestmove
        return score, x, y

    # 返回最优下棋点
    def findBestChess(self, board, turn):
        time1 = time.time()
        score, x, y = self.search(board, turn, AI_SEARCH_DEPTH)
        time2 = time.time()
        return x, y

    # 返回count形成的所有棋型的分数
    def getPointScore(self, count):
        score = 0
        if count[FIVE] > 0:
            return SCORE_FIVE * count[FIVE]

        if count[FOUR] > 0:
            return SCORE_FOUR * count[FOUR]

        if count[SFOUR] > 1:
            score += count[SFOUR] * SCORE_SFOUR
        elif count[SFOUR] > 0 and count[THREE] > 0:
            score += count[SFOUR] * SCORE_SFOUR
        elif count[SFOUR] > 0:
            score += SCORE_THREE

        if count[THREE] > 1:
            score += 5 * SCORE_THREE
        elif count[THREE] > 0:
            score += SCORE_THREE

        if count[STHREE] > 0:
            score += count[STHREE] * SCORE_STHREE
        if count[TWO] > 0:
            score += count[TWO] * SCORE_TWO
        if count[STWO] > 0:
            score += count[STWO] * SCORE_STWO

        return score

    # 通过己方形成的棋型和对手的棋型对形式进行打分
    def getScore(self, mine_count, opponent_count):
        mscore, oscore = 0, 0
        if mine_count[FIVE] > 0:
            return SCORE_FIVE, 0
        if opponent_count[FIVE] > 0:
            return 0, SCORE_FIVE
        mine_count[FOUR] += mine_count[SFOUR] / 2
        opponent_count[FOUR] += opponent_count[SFOUR] / 2
        if mine_count[FOUR] > 0:
            return 9050, 0
        if mine_count[SFOUR] > 0:
            return 9040, 0
        if opponent_count[FOUR] > 0:
            return 0, 9030
        if opponent_count[SFOUR] > 0 and opponent_count[THREE] > 0:
            return 0, 9020
        if mine_count[THREE] > 0 and opponent_count[SFOUR] == 0:
            return 9010, 0
        if opponent_count[THREE] > 0 and mine_count[SFOUR] == 0:
            return 0, 9000
        if mine_count[THREE] > 1 and opponent_count[THREE] == 0 and opponent_count[STHREE] == 0:
            return 8990, 0
        if opponent_count[THREE] > 1 and mine_count[THREE] == 0 and mine_count[STHREE] == 0:
            return 0, 8980
        if opponent_count[SFOUR] > 0:
            oscore += 400
        if mine_count[THREE] > 1:
            mscore += 2500
        elif mine_count[THREE] > 0:
            mscore += 500
        if opponent_count[THREE] > 1:
            oscore += 2000
        elif opponent_count[THREE] > 0:
            oscore += 400
        if mine_count[STHREE] > 0:
            mscore += mine_count[STHREE] * 10
        if opponent_count[STHREE] > 0:
            oscore += opponent_count[STHREE] * 10
        if mine_count[TWO] > 0:
            mscore += mine_count[TWO] * 6
        if opponent_count[TWO] > 0:
            oscore += opponent_count[TWO] * 6
        if mine_count[STWO] > 0:
            mscore += mine_count[STWO] * 2
        if opponent_count[STWO] > 0:
            oscore += opponent_count[STWO] * 2
        return mscore, oscore

    # 返回当前对于turn的优势程度
    def evaluate(self, board, turn, checkWin=False):
        self.reset()
        if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
            mine = 1
            opponent = 2
        else:
            mine = 2
            opponent = 1
        # 将所有棋型的数量记录在count中,会在evaluatePoint中记录每个点的棋型
        for y in range(self.len):
            for x in range(self.len):
                if board[y][x] == mine:
                    self.evaluatePoint(board, x, y, mine, opponent)
                elif board[y][x] == opponent:
                    self.evaluatePoint(board, x, y, opponent, mine)
        mine_count = self.count[mine - 1]
        opponent_count = self.count[opponent - 1]
        if checkWin:
            return mine_count[FIVE] > 0
        else:
            # 所以棋型的分数计算后相减返回
            mscore, oscore = self.getScore(mine_count, opponent_count)
            return mscore - oscore


    # 计算x,y点的四个方向的棋型
    def evaluatePoint(self, board, x, y, mine, opponent, count=None):
        if self.isBalance:
            if mine == MAP_ENTRY_TYPE.MAP_PLAYER_ONE and self.isBalanceBreaker(board, x,
                                                                               y) != Balance_Breaker_Type.NONE:
                return
        dir_offset = [(1, 0), (0, 1), (1, 1), (1, -1)]
        ignore_record = True
        if count is None:
            count = self.count[mine - 1]
            ignore_record = False
        for i in range(4):
            if self.record[y][x][i] == 0 or ignore_record:
                self.analysisLine(board, x, y, i, dir_offset[i], mine, opponent, count)

    # 对一个点的dir方向上的棋型进行判断
    def analysisLine(self, board, x, y, dir_index, dir, mine, opponent, count):
        # 用来记录已被判断其棋型的棋子防止重复计算
        def setRecord(self, x, y, left, right, dir_index, dir_offset):
            tmp_x = x + (-5 + left) * dir_offset[0]
            tmp_y = y + (-5 + left) * dir_offset[1]
            for i in range(left, right + 1):
                tmp_x += dir_offset[0]
                tmp_y += dir_offset[1]
                self.record[tmp_y][tmp_x][dir_index] = 1

        empty = MAP_ENTRY_TYPE.MAP_EMPTY.value
        # 记录最左最右的棋子的下标
        left_idx, right_idx = 4, 4

        # 将dir方向上x,y点形成的行返回
        line = self.getLine(board, x, y, dir, mine, opponent)

        while right_idx < 8:
            if line[right_idx + 1] != mine:
                break
            right_idx += 1
        while left_idx > 0:
            if line[left_idx - 1] != mine:
                break
            left_idx -= 1

        left_range, right_range = left_idx, right_idx
        while right_range < 8:
            if line[right_range + 1] == opponent:
                break
            right_range += 1
        while left_range > 0:
            if line[left_range - 1] == opponent:
                break
            left_range -= 1

        chess_range = right_range - left_range + 1
        if chess_range < 5:
            setRecord(self, x, y, left_range, right_range, dir_index, dir)
            return CHESS_TYPE.NONE

        setRecord(self, x, y, left_idx, right_idx, dir_index, dir)

        m_range = right_idx - left_idx + 1

        if m_range >= 5:
            count[FIVE] += 1

        if m_range == 4:
            left_empty = right_empty = False
            if line[left_idx - 1] == empty:
                left_empty = True
            if line[right_idx + 1] == empty:
                right_empty = True
            if left_empty and right_empty:
                count[FOUR] += 1
            elif left_empty or right_empty:
                count[SFOUR] += 1

        if m_range == 3:
            left_empty = right_empty = False
            left_four = right_four = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:
                    count[SFOUR] += 1
                    left_four = True
                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:
                    setRecord(self, x, y, right_idx + 1, right_idx + 2, dir_index, dir)
                    count[SFOUR] += 1
                    right_four = True
                right_empty = True

            if left_four or right_four:
                pass
            elif left_empty and right_empty:
                if chess_range > 5:
                    count[THREE] += 1
                else:
                    count[STHREE] += 1
            elif left_empty or right_empty:
                count[STHREE] += 1

        if m_range == 2:
            left_empty = right_empty = False
            left_three = right_three = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:
                    if line[left_idx - 3] == mine:
                        count[SFOUR] += 1
                    elif line[left_idx - 3] == empty:
                        if line[right_idx + 1] == empty:
                            count[THREE] += 1
                        else:
                            count[STHREE] += 1
                        left_three = True
                    elif line[left_idx - 3] == opponent:
                        if line[right_idx + 1] == empty:
                            count[STHREE] += 1
                            left_three = True
                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:
                    setRecord(self, x, y, right_idx + 2, right_idx + 2, dir_index, dir)
                    if line[right_idx + 3] == mine:
                        setRecord(self, x, y, right_idx + 3, right_idx + 3, dir_index, dir)
                        count[SFOUR] += 1
                        right_three = True
                    elif line[right_idx + 3] == empty:
                        if left_empty:
                            count[THREE] += 1
                        else:
                            count[STHREE] += 1
                        right_three = True
                    elif left_empty:
                        count[STHREE] += 1
                        right_three = True

                right_empty = True

            if left_three or right_three:
                pass
            elif left_empty and right_empty:
                count[TWO] += 1
            elif left_empty or right_empty:
                count[STWO] += 1

        if m_range == 1:
            left_empty = right_empty = False
            left_three1 = right_three1 = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == mine:
                    if line[left_idx - 3] == mine:
                        if line[left_idx - 4] == mine:
                            count[SFOUR] += 1
                        elif line[left_idx - 4] == empty and line[right_idx + 1] == empty:
                            count[THREE] += 1
                        else:
                            count[STHREE] += 1
                    if line[left_idx - 3] == empty:
                        if line[right_idx + 1] == empty:
                            count[TWO] += 1
                        else:
                            count[STWO] += 1
                    else:
                        if line[right_idx + 1] == empty:
                            count[STWO] += 1

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == mine:
                    if line[right_idx + 3] == mine:
                        if line[right_idx + 4] == mine:
                            setRecord(self, x, y, right_idx + 2, right_idx + 4, dir_index, dir)
                            count[SFOUR] += 1
                        elif line[right_idx + 4] == empty and line[left_idx - 1] == empty:
                            setRecord(self, x, y, right_idx + 2, right_idx + 3, dir_index, dir)
                            count[THREE] += 1
                        else:
                            setRecord(self, x, y, right_idx + 2, right_idx + 3, dir_index, dir)
                            count[STHREE] += 1
                    if line[right_idx + 3] == empty:
                        if line[left_idx - 1] == empty:
                            setRecord(self, x, y, right_idx + 2, right_idx + 2, dir_index, dir)
                            count[TWO] += 1
                        else:
                            setRecord(self, x, y, right_idx + 2, right_idx + 2, dir_index, dir)
                            count[STWO] += 1
                    else:
                        if line[left_idx - 1] == empty:
                            setRecord(self, x, y, right_idx + 2, right_idx + 2, dir_index, dir)
                            count[STWO] += 1

        return CHESS_TYPE.NONE

    # 判断此处是否为禁手
    def isBalanceBreaker(self, board, x, y):
        player = MAP_ENTRY_TYPE.MAP_PLAYER_ONE
        computer = MAP_ENTRY_TYPE.MAP_PLAYER_TWO
        dir_offset = [(1, 0), (0, 1), (1, 1), (1, -1)]  # direction from left to right
        empty = MAP_ENTRY_TYPE.MAP_EMPTY.value
        # 五连个数
        five = 0
        # 长连的个数
        longlink = 0
        # 活四个数
        four = 0
        # 三连个数
        three = 0
        for dir in dir_offset:
            # 分别记录在line中以x,y为中心的到最右和最左的连续的为mine的棋子的下标
            left_idx, right_idx = 5, 5
            # 将当前x,y点的dir方向上的10个棋子作为数组返回
            line = self.getLine(board, x, y, dir, player, computer, lens=11)
            # print(line)
            while right_idx < 10:
                if line[right_idx + 1] != player:
                    break
                right_idx += 1
            while left_idx > 0:
                if line[left_idx - 1] != player:
                    break
                left_idx -= 1
            # 分别记录在line中以x,y为中心的到最右和最左的连续的为空位置的下标
            left_range, right_range = left_idx, right_idx
            while right_range < 10:
                if line[right_range + 1] == computer:
                    break
                right_range += 1
            while left_range > 0:
                if line[left_range - 1] == computer:
                    break
                left_range -= 1
            # 计算当前连子的个数
            m_range = right_idx - left_idx + 1

            # 获得当前方向上违背封堵的可形成的最长的mine的棋子的长度
            chess_range = right_range - left_range + 1

            # 若当前连子大于5则说明此处为长连
            if m_range > 5:
                longlink += 1
                continue

            # 若当前连子大于5则说明为连5
            if m_range == 5:
                five += 1
                continue

            # 判断四子相连的情况
            if m_range == 4:
                left_empty = right_empty = False
                if line[left_idx - 1] == empty:
                    left_empty = True
                if line[right_idx + 1] == empty:
                    right_empty = True
                if left_empty and right_empty:
                    four += 1
                elif left_empty or right_empty:
                    four += 1
                continue

            # 判断三子相连的情况
            if m_range == 3:
                left_empty = right_empty = False
                left_four = right_four = False
                if line[left_idx - 1] == empty:
                    if line[left_idx - 2] == player:  # MXMMM
                        four += 1
                        left_four = True
                    left_empty = True

                if line[right_idx + 1] == empty:
                    if line[right_idx + 2] == player:  # MMMXM
                        four += 1
                        right_four = True
                    right_empty = True

                if left_four or right_four:
                    pass
                elif left_empty and right_empty:
                    if chess_range > 5:  # XMMMXX, XXMMMX
                        three += 1
                continue

            # 判断两子相连的情况
            if m_range == 2:
                left_empty = right_empty = False
                left_three = right_three = False
                if line[left_idx - 1] == empty:
                    if line[left_idx - 2] == player:
                        if line[left_idx - 3] == empty:
                            if line[right_idx + 1] == empty:  # XMXMMX
                                three += 1
                            left_three = True
                        elif line[left_idx - 3] == player:  # PMXMMX
                            four += 1
                    left_empty = True

                if line[right_idx + 1] == empty:
                    if line[right_idx + 2] == player:
                        if line[right_idx + 3] == player:  # MMXMM
                            four += 1
                            right_three = True
                        elif line[right_idx + 3] == empty:
                            # setRecord(self, x, y, right_idx+1, right_idx+2, dir_index, dir)
                            if left_empty:  # XMMXMX
                                three += 1
                continue
            # 判断当前连子为1个的情况
            if m_range == 1:
                left_empty = right_empty = False

                if line[left_idx - 1] == empty:
                    if line[left_idx - 2] == player and line[left_idx - 3] == player:
                        if line[left_idx - 4] == empty and line[right_idx + 1] == empty:
                            three += 1
                        elif line[left_idx - 4] == player:
                            four += 1
                    left_empty = True

                if line[right_idx + 1] == empty:
                    if line[right_idx + 2] == player and line[right_idx + 3] == player:
                        if line[right_idx + 4] == empty and left_empty:
                            three += 1
                        elif line[right_idx + 4] == player:
                            four += 1
                continue
        # 若禁手与连5同时发生,禁手失效直接返回
        if five >= 1:
            return Balance_Breaker_Type.NONE
        if longlink >= 1:
            # print("longlink")
            return Balance_Breaker_Type.LONG_LINK
        if four >= 2:
            return Balance_Breaker_Type.FOUR_FOUR
        if three >= 2:
            return Balance_Breaker_Type.THREE_THREE
        return CHESS_TYPE.NONE

    # 随机下棋
    def __search1(self, board, turn, depth, alpha=SCORE_MIN, beta=SCORE_MAX):
        score = 0
        moves = self.genmove1(board, turn)
        index = randint(0, len(moves) - 1)
        _, x, y = moves[index]
        self.bestmove = (x, y)
        return 0

    # 返回所有非空的节点
    def genmove1(self, board, turn):
        moves = []
        for y in range(self.len):
            for x in range(self.len):
                if board[y][x] == 0:
                    moves.append((0, x, y))
        moves.sort(reverse=True)
        return moves

    # 判断是否胜利
    def isAlreadyWin(self, board, x, y, mine, op):
        dir_offset = [(1, 0), (0, 1), (1, 1), (1, -1)]  # direction from left to right
        for dir in dir_offset:
            # 分别记录在line中以x,y为中心的到最右和最左的连续的为mine的棋子的下标
            left_idx, right_idx = 5, 5
            # 将当前x,y点的dir方向上的10个棋子作为数组返回
            line = self.getLine(board, x, y, dir, mine, op, lens=11)
            while right_idx < 10:
                if line[right_idx + 1] != mine:
                    break
                right_idx += 1
            while left_idx > 0:
                if line[left_idx - 1] != mine:
                    break
                left_idx -= 1
            # 分别记录在line中以x,y为中心的到最右和最左的连续的为空位置的下标
            left_range, right_range = left_idx, right_idx
            while right_range < 10:
                if line[right_range + 1] == op:
                    break
                right_range += 1
            while left_range > 0:
                if line[left_range - 1] == op:
                    break
                left_range -= 1
            # 计算当前连子的个数
            m_range = right_idx - left_idx + 1

            # 获得当前方向上违背封堵的可形成的最长的mine的棋子的长度
            chess_range = right_range - left_range + 1

            if m_range >= 5:
                return True
        return False

    # 按坐标和方向返回棋盘中对应的一行
    def getLine(self, board, x, y, dir_offset, mine, opponent, lens=9):
        line = [0 for i in range(lens)]

        tmp_x = x + (-(lens // 2 + 1) * dir_offset[0])
        tmp_y = y + (-(lens // 2 + 1) * dir_offset[1])
        for i in range(lens):
            tmp_x += dir_offset[0]
            tmp_y += dir_offset[1]
            if (tmp_x < 0 or tmp_x >= self.len or
                    tmp_y < 0 or tmp_y >= self.len):
                line[i] = opponent  # set out of range as opponent chess
            else:
                line[i] = board[tmp_y][tmp_x]

        return line
