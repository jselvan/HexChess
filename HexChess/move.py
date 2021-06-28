from HexChess.enums import ChessmanName
from HexChess.hex import Hex

from pyparsing import Word, Optional, Literal, Group, nums

chessman_notation ={
    ChessmanName.pawn: '',
    ChessmanName.bishop: 'B',
    ChessmanName.knight: 'N',
    ChessmanName.rook: 'R',
    ChessmanName.queen: 'Q',
    ChessmanName.king: 'K'
}
chessman_notation_rev = dict((v,k) for k,v in chessman_notation.items())
class Move:
    def __init__(self, origin, target, capture=False, enpassant=False, promote=False, promote_piece=None):
        self.origin = origin
        self.target = target
        self.capture = capture
        self.enpassant = enpassant
        self.promote = promote
        self.promote_piece = '0' if promote_piece is None else promote_piece
        self.bytes = self.dump()
    def get_promote_piece(self):
        from HexChess.chessman import newChessman
        return newChessman(int(self.promote_piece, 16))
    def __hash__(self):
        return hash(self.bytes)
    def __eq__(self, other):
        return self.bytes == other.bytes
    def __ne__(self, other):
        return not self.__eq__(other)
    def dump(self):
        info = (self.capture  << 3) \
            + (self.enpassant << 2) \
            + (self.promote   << 1)
        return bytes.fromhex(self.origin.hex() + self.target.hex() + hex(info)[-1] + self.promote_piece)
    @classmethod
    def load(cls, input_bytes):
        data = hex(int.from_bytes(input_bytes,'big'))[2:]
        origin, target = Hex.from_hex(data[:2]), Hex.from_hex(data[2:4])
        info = int(data[4], 16)
        capture = bool(info & 8)
        enpassant = bool(info & 4)
        promote = bool(info & 2)
        promote_piece = data[5] if promote else None
        return cls(origin, target, capture, enpassant, promote, promote_piece)
    def notation(self, game):
        piece = game.board.pieces[self.origin]
        notation = chessman_notation[piece.name]
        for other_piece in game.board.pieces.values():
            if other_piece.name is piece.name:
                for move in other_piece.moves:
                    if move.target == self.target:
                        notation += self.origin.notation
        if self.capture:
            notation += 'x'
        notation += self.target.notation
        if self.promote:
            notation += chessman_notation[self.get_promote_piece().name]
        if self.enpassant:
            notation += ' e.p.'
    @classmethod
    def from_notation(self, notation, game):
        TILE = Word('abcdefghikl',exact=1)+Word(nums,exact=1)
        PIECE = Word('BNRQK',exact=1)
        notation_parser = Optional(PIECE, default=None)\
            + Optional(Group(TILE), default=None)\
            + Optional('x', default=None)\
            + Optional(Group(TILE), default=None)\
            + Optional(Literal(' e.p.') | PIECE, default=None)
        piece, origin, capture, target, special = notation_parser.parseString(notation)

        if capture is None and target is None:
            origin, target = None, origin
        target = Hex.from_notation(''.join(target))
        if origin is None:
            piece_name = chessman_notation_rev.get(piece, ChessmanName.pawn)
            piece_colour = game.turn_colour
            for origin, piece in game.board.pieces.items():
                if piece is not None \
                    and piece.name is piece_name \
                    and piece.colour is piece_colour \
                    and target in (move.target for move in piece.moves):
                    break
            else:
                raise ValueError #TODO: Make this a custom error?
        else:
            origin = Hex.from_notation(''.join(origin))
        capture = capture is not None

        enpassant = False
        promote = False
        promote_piece = None
        if special is None:
            pass
        elif special == ' e.p.':
            enpassant = True
        else:
            promote = True
            promote_piece = hex(game.turn_colour.value + chessman_notation_rev[special].value)[-1]
        #TODO: test this out
        return Move(origin, target, capture=capture, enpassant=enpassant, promote=promote, promote_piece=promote_piece)