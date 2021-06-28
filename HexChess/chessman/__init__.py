from HexChess.enums import ChessmanName, PlayerColour
from HexChess.chessman.pawn import Pawn
from HexChess.chessman.bishop import Bishop
from HexChess.chessman.knight import Knight
from HexChess.chessman.rook import Rook
from HexChess.chessman.queen import Queen
from HexChess.chessman.king import King
chessman_map = {
    ChessmanName.pawn: Pawn,
    ChessmanName.bishop: Bishop,
    ChessmanName.knight: Knight,
    ChessmanName.rook: Rook,
    ChessmanName.queen: Queen,
    ChessmanName.king: King,
}
def newChessman(inputbits):
    return chessman_map[ChessmanName(inputbits&7)](colour=PlayerColour(inputbits&8))