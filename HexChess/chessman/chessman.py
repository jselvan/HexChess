#TODO: rangers are not showing all moves
from HexChess.hex import Hex
from HexChess.enums import ChessmanName
from HexChess.move import Move

promote_pieces = ChessmanName.queen,ChessmanName.rook,ChessmanName.bishop,ChessmanName.knight 
class Chessman:
    ranger = False
    def __init__(self, colour):
        self.colour = colour
        self.is_reinforced = False
    @property
    def hex(self):
        return hex(self.colour.value + self.name.value)[-1]
    def add_move(self, pos, capture=False, enpassant=False, promote=False):
        if promote:
            for piece in promote_pieces:
                self.moves.add(Move(self.current_position, pos, capture=capture, promote=True, promote_piece=hex(self.colour.value+piece.value)[-1]))
        else:
            self.moves.add(Move(self.current_position, pos, capture=capture, enpassant=enpassant))
    def reset(self):
        self.is_pinned = False
        self.pin_piece = None
        self.pinned_allowed = set()
        self.moves = set()
    def check_move(self, pos, dv, game):
        board = game.board.pieces
        moves = set()
        while True:
            pos += dv
            if pos not in board: break
            tile = board[pos]
            if tile is None:
                moves.add(pos)
                if not self.ranger: break
            elif tile.colour is self.colour:
                tile.is_reinforced = True
                break
            elif tile.name is ChessmanName.king:
                if game.check:
                    game.check_block_range = set()
                    game.check_piece = None
                else:
                    game.check = True
                    game.check_block_range = moves
                    game.check_piece = self
                next_pos = pos+dv
                if self.ranger and next_pos in board and self.colour is not game.turn_colour:
                    game.king_danger_zone.add(next_pos)
                break
            else:
                if game.check and tile != game.check_piece: break
                if self.ranger:
                    next_pos = pos+dv
                    while next_pos in board:
                        next_tile = board[next_pos]
                        if next_tile is None:
                            next_pos += dv
                            continue
                        elif next_tile.name is ChessmanName.king and next_tile.colour is not self.colour:
                            tile.is_pinned = True
                            tile.pinned_allowed = moves
                            tile.pin_piece = self
                            break
                        else:
                            break
                self.add_move(pos, capture=True)
                break
        for move in moves:
            if self.colour is not game.turn_colour: game.king_danger_zone.add(move)
            if self.is_pinned: continue
            if game.check and move not in game.check_block_range: continue
            self.add_move(move)
    def get_moves(self, pos, game):
        self.current_position = pos
        for dv in self.DV:
            self.check_move(pos, dv, game)