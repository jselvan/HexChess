from HexChess.move import Move
from HexChess.enums import PlayerColour, get_opponent
from HexChess.board import Board
starting_board = b'\xb0\x00\t\t\x90\x000\x90\x00\xa0\x90\x91\x10\xb0\xa0\x19\xb0\xc9\x00\x00\x90\x00\x00\x00\x00\x00@\x00\x00\x00\x03\x12A\x1eb\xc0\x00\x00\x00\r\x10\x01\x00\x010P'

class InvalidMoveError(Exception):
    pass

class Game:
    opponent = {0:8, 8:0}
    def __init__(self, board=None, turn_history=None):
        self.game_state = 'ongoing'
        if board is None:
            self.board = Board.load(starting_board)
        else:
            self.board = board
        if turn_history is None:
            self.turn_history = bytes(0)
        else:
            self.turn_history = turn_history
        self.get_all_moves()
    def conduct_move(self, move: Move):
        if self.game_state != 'ongoing':
            raise ValueError('Game is already finished!')
        elif move.origin not in self.board.pieces:
            raise InvalidMoveError
        elif move not in self.board.pieces[move.origin].moves:
            raise InvalidMoveError
        if move.promote:
            self.board.pieces[move.origin], self.board.pieces[move.target] = None, move.get_promote_piece()
        else:
            if move.enpassant:
                captured_pawn_loc = move.target+self.board.pieces[move.origin].OPPONENT_DV[self.turn_colour]
                self.board.pieces[captured_pawn_loc] = None
            self.board.pieces[move.origin], self.board.pieces[move.target] = None, self.board.pieces[move.origin]
        self.turn_history += move.bytes
        self.get_all_moves()
    def dump(self) -> bytes:
        return self.board.dump() + self.turn_history
    @classmethod
    def load(cls, input_bytes: bytes):
        board = Board.load(input_bytes[:92])
        return cls(board, turn_history=input_bytes[92:])
    @property
    def turn(self) -> int:
        return int(len(self.turn_history) // 3)
    @property
    def turn_colour(self) -> PlayerColour:
        return PlayerColour( self.turn%2<<3 )
    def get_all_moves(self):
        ## RESET VARIABLES
        self.king_danger_zone = set()
        self.check = False
        self.check_block_range = set()
        self.check_piece = None
        for piece in self.board.pieces.values():
            if piece is not None: piece.reset()
        ## GRAB ALL MOVES
        for colour in [get_opponent(self.turn_colour), self.turn_colour]:
            for position, piece in self.board.pieces.items():
                if piece is not None and piece.colour is colour: 
                    piece.get_moves(position, self)
        ## UPDATE GAME STATEs
        self.check_game_state()
    def check_game_state(self):
        for piece in self.board.pieces.values():
            if piece is None: continue
            if piece.colour is self.turn_colour and piece.moves: break
        else:
            if self.check:
                self.game_state = self.turn_colour.name + 'wins'
            else:
                self.game_state = 'draw'