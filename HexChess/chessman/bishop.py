from HexChess.enums import ChessmanName
from HexChess.chessman.chessman import Chessman
from HexChess.hex import hex_diagonals
class Bishop(Chessman):
    name = ChessmanName.bishop
    ranger = True
    DV = hex_diagonals