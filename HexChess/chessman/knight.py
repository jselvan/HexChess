from HexChess.hex import Hex
from HexChess.enums import ChessmanName
from HexChess.chessman.chessman import Chessman
class Knight(Chessman):
    name = ChessmanName.knight
    DV = (
        Hex( 1,-3), Hex( 2,-3), Hex( 3,-2), Hex( 3,-1),
        Hex( 2, 1), Hex( 1, 2), Hex(-1, 3), Hex(-2, 3),
        Hex(-3, 2), Hex(-3, 1), Hex(-2,-1), Hex(-1,-2)
    )