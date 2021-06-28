from enum import Enum

class PlayerColour(Enum):
    white = 0
    black = 8
class ChessmanName(Enum):
    pawn = 1
    knight = 2
    bishop = 3
    rook = 4
    queen = 5
    king = 6

opponent = {0:8,8:0}
def get_opponent(playercolour):
    return PlayerColour(opponent[PlayerColour(playercolour).value])