from HexChess.enums import ChessmanName
from HexChess.chessman.chessman import Chessman
from HexChess.hex import hex_directions, hex_diagonals
class King(Chessman):
    name = ChessmanName.king
    DV = hex_directions | hex_diagonals
    def get_moves(self, pos, game):
        self.current_position = pos
        board = game.board.pieces
        for dv in self.DV:
            new_pos = pos + dv
            if new_pos not in board or new_pos in game.king_danger_zone: continue
            piece = board[new_pos]
            if piece is None:
                if self.colour is not game.turn_colour: game.king_danger_zone.add(new_pos)
                self.add_move(new_pos)
            elif piece.colour is self.colour:
                piece.is_reinforced = True
            elif not piece.is_reinforced:
                #TODO: check this is not working...
                self.add_move(new_pos, capture=True)