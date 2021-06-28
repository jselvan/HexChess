from HexChess.move import Move
from HexChess.hex import Hex
from HexChess.enums import ChessmanName, PlayerColour
from HexChess.chessman.chessman import Chessman
class Pawn(Chessman):
    DV = {
        PlayerColour.white: Hex(0,-1),
        PlayerColour.black: Hex(0, 1),
    }
    CAPTURE_DV = {
        PlayerColour.white: (Hex(-1,0), Hex(1,-1)),
        PlayerColour.black: (Hex(-1,1), Hex(1, 0)),
    }
    OPPONENT_DV = {
        PlayerColour.white: Hex(0, 1), 
        PlayerColour.black: Hex(0,-1)
    } 
    name = ChessmanName.pawn
    DIRECTION = {PlayerColour.white:1, PlayerColour.black:-1}
    def get_moves(self, pos, game):
        self.current_position = pos
        direction = self.DIRECTION[self.colour]
        board = game.board.pieces
        forward = pos + self.DV[self.colour]
        double_step = forward + self.DV[self.colour]
        captures = [pos+DV for DV in self.CAPTURE_DV[self.colour]]

        if not self.is_pinned and forward in board and board[forward] is None:
            if not game.check or forward in game.check_block_range: 
                self.add_move(forward,promote=forward.rank(direction)==11)
            if pos.rank(direction)==5 and board[double_step] is None:
                if not game.check or double_step in game.check_block_range:
                    self.add_move(double_step)
        
        for capture in captures:
            if capture in board:
                piece = board[capture]
                if piece is None:
                    if self.colour is not game.turn_colour: 
                        game.king_danger_zone.add(capture)
                    if game.turn_history:
                        last_move = Move.load(game.turn_history[-3:])
                        last_moved_piece = game.board.pieces[last_move.target]
                        
                        ### EN PASSANT LOGIC
                        # check if is (1) pawn, of (2) enemy colour
                        # that is (3) ahead of capture spot 
                        # and (4) started behind capture spot 
                        # and standard check/pin checks
                        # Iff all true, this is a legal en passant 
                        if last_moved_piece.name is ChessmanName.pawn\
                            and last_moved_piece.colour is not self.colour\
                            and last_move.target == capture+self.OPPONENT_DV[self.colour]\
                            and last_move.origin == capture+self.DV[self.colour]\
                            and (not game.check or piece is game.check_piece)\
                            and (not self.is_pinned or piece is self.pin_piece):
                            self.add_move(capture, capture=True, enpassant=True) 

                elif piece.colour is self.colour:
                    piece.is_reinforced = True
                elif piece.name is ChessmanName.king:
                    if game.check:
                        game.check_piece = None
                        game.check_block_range = set()
                    else:
                        game.check = True
                        game.check_piece = self
                else:
                    if (not game.check or piece is game.check_piece) \
                        and (not self.is_pinned or piece is self.pin_piece):
                        self.add_move(capture,capture=True,promote=capture.rank(direction)==11)