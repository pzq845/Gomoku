from enum import IntEnum


class CHESS_TYPE(IntEnum):
    NONE = 0,
    SLEEP_TWO = 1,
    LIVE_TWO = 2,
    SLEEP_THREE = 3
    LIVE_THREE = 4,
    CHONG_FOUR = 5,
    LIVE_FOUR = 6,
    LIVE_FIVE = 7,


# 棋型的枚举
class Balance_Breaker_Type(IntEnum):
    NONE = 0,
    THREE_THREE = 1,
    FOUR_FOUR = 2,
    LONG_LINK = 3


Breaker_InfoDir = {Balance_Breaker_Type.THREE_THREE: "三三禁手",
                   Balance_Breaker_Type.FOUR_FOUR: "四四禁手",
                   Balance_Breaker_Type.LONG_LINK: "长连禁手"}

CHESS_TYPE_NUM = 8

FIVE = CHESS_TYPE.LIVE_FIVE.value
FOUR, THREE, TWO = CHESS_TYPE.LIVE_FOUR.value, CHESS_TYPE.LIVE_THREE.value, CHESS_TYPE.LIVE_TWO.value
SFOUR, STHREE, STWO = CHESS_TYPE.CHONG_FOUR.value, CHESS_TYPE.SLEEP_THREE.value, CHESS_TYPE.SLEEP_TWO.value

# SCORE_MAX = 0x7fffffff
# SCORE_MIN = -1 * SCORE_MAX
# SCORE_FIVE, SCORE_FOUR, SCORE_SFOUR = 100000, 10000, 1000
# SCORE_THREE, SCORE_STHREE, SCORE_TWO, SCORE_STWO = 100, 10, 8, 2

# 设定棋型的分数
SCORE_MAX = 1000000
SCORE_MIN = -1 * SCORE_MAX
SCORE_FIVE, SCORE_FOUR, SCORE_SFOUR = 100000, 10000, 1000
SCORE_THREE, SCORE_STHREE, SCORE_TWO, SCORE_STWO = 100, 10, 5, 2
