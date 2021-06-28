from HexChess.enums import ChessmanName
from HexChess.chessman.chessman import Chessman
from HexChess.hex import hex_directions
class Rook(Chessman):
    name = ChessmanName.rook
    ranger = True
    DV = hex_directions