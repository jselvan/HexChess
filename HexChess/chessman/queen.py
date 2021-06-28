from HexChess.enums import ChessmanName
from HexChess.chessman.chessman import Chessman
from HexChess.hex import hex_diagonals, hex_directions
class Queen(Chessman):
    name = ChessmanName.queen
    ranger = True
    DV = hex_directions | hex_diagonals