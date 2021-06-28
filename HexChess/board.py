from HexChess.util import colourstring
from HexChess.hex import ORIENTATIONS, Layout, Point, get_radially_symmetric_hexagonal_board
from HexChess.enums import PlayerColour, ChessmanName
from HexChess.chessman import newChessman

from itertools import product


ascii_extended_map = {
    (PlayerColour.white, ChessmanName.pawn): u'\u265F',
    (PlayerColour.white, ChessmanName.rook): u'\u265C',
    (PlayerColour.white, ChessmanName.knight): u'\u265E',
    (PlayerColour.white, ChessmanName.bishop): u'\u265D',
    (PlayerColour.white, ChessmanName.king): u'\u265A',
    (PlayerColour.white, ChessmanName.queen): u'\u265B',
    (PlayerColour.black, ChessmanName.pawn): u'\u2659',
    (PlayerColour.black, ChessmanName.rook): u'\u2656',
    (PlayerColour.black, ChessmanName.knight): u'\u2658',
    (PlayerColour.black, ChessmanName.bishop): u'\u2657',
    (PlayerColour.black, ChessmanName.king): u'\u2654',
    (PlayerColour.black, ChessmanName.queen): u'\u2655'
}

class Board:
    RADIUS = 5
    ORIENTATION = 'flat'
    tiles = sorted(get_radially_symmetric_hexagonal_board(RADIUS))
    def __init__(self):
        self.pieces = {tile: None for tile in self.tiles}
        self.colours = {tile: (tile.x-tile.y)%3 for tile in self.tiles}
    def dump(self):
        return bytes.fromhex("".join(['0' if self.pieces[tile] is None else self.pieces[tile].hex for tile in self.tiles]) + "0")
    @classmethod
    def load(cls, input_bytes):
        self = cls()
        pieces = hex(int.from_bytes(input_bytes,'big'))[2:-1]
        for tile, piece in zip(self.tiles, pieces):
            piece = int(piece,16)
            if piece:
                self.pieces[tile] = newChessman(piece)
        return self
    def get_layout(self, size, origin):
        layout = Layout(
            ORIENTATIONS[self.ORIENTATION],
            size = Point(*size),
            origin = Point(*origin)
        )
        return layout
    def draw(self, backend='ascii+'):
        if backend == 'ascii+':
            self._draw_ascii()
    def _get_chr(self, x, y):
        if 0 < x < 4 and y in [0,2]: return '_'
        elif (x==0 and y==1) or (x==4 and y==2): return '/'
        elif (x==0 and y==2) or (x==4 and y==1): return '\\'
        elif x==2 and y==1: return '+'
    def _draw_ascii(self, extended=True):
        n = self.RADIUS*2+1
        X, Y = n*4+1, n*2+1
        oX, oY = n//2*4, n//2*2
        board = [[' ' for _ in range(X)] for _ in range(Y)]
        layout = Layout(ORIENTATIONS['flat_ascii'], Point(1,1), Point(oX,oY))

        X, Y = 5, 3
        for hex, piece in self.pieces.items():
            anchor = hex.to_pixel(layout)
            for x, y in product(range(X),range(Y)):
                character = self._get_chr(x, y)
                if character is None: continue
                if character=='+':
                    character = ' ' if piece is None else ascii_extended_map[piece.colour, piece.name]
                board[anchor.y+y][anchor.x+x] = character
                
        board = "\n".join(["".join(row) for row in board])
        print(board)

    @staticmethod
    def _get_chr_coords(x, y):
        if 0 < x < 4 and y in [0,2]: return '_'
        elif (x==0 and y==1) or (x==4 and y==2): return '/'
        elif (x==0 and y==2) or (x==4 and y==1): return '\\'
        elif x==1 and y==1: return 'X'
        elif x==2 and y==1: return 'Y'
        elif x==3 and y==1: return 'Z'
    @classmethod
    def _draw_ascii_coords(cls, type='xyz'):
        n = cls.RADIUS*2+1
        X, Y = n*4+1, n*2+1
        oX, oY = n//2*4, n//2*2
        board = [[' ' for _ in range(X)] for _ in range(Y)]
        layout = Layout(ORIENTATIONS['flat_ascii'], Point(1,1), Point(oX,oY))

        X, Y = 5, 3
        for tile in cls.tiles:
            if type=='xyz':
                xstr = colourstring(abs(tile.x), 'GREEN' if tile.x>=0 else 'RED')
                ystr = colourstring(abs(tile.y), 'GREEN' if tile.y>=0 else 'RED')
                zstr = colourstring(abs(tile.z), 'GREEN' if tile.z>=0 else 'RED')
            elif type=='cr':
                xstr, ystr, zstr = tile.col, str(tile.row), ' '
            anchor = tile.to_pixel(layout)
            for x, y in product(range(X),range(Y)):
                character = cls._get_chr_coords(x, y)
                if character is not None:
                    if character=='X': character=xstr
                    if character=='Y': character=ystr
                    if character=='Z': character=zstr
                    board[anchor.y+y][anchor.x+x] = character
                
        board = "\n".join(["".join(row) for row in board])
        print(board)