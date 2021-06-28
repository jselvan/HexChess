#TODO: now double check all movement logic
from HexChess.chessman import newChessman
from HexChess.board import Board
from HexChess import RESOURCEPATH
from HexChess.enums import PlayerColour, ChessmanName
from HexChess.hex import Layout, ORIENTATIONS, Point, Hex
from HexChess.game import Game
from HexChess.move import Move

from PIL import Image
import pygame

DARK = (210,140,70)
MID = (230,170,110)
LITE = (255,200,150)
WHITE = (255,255,255)
GREY = (205,205,205)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0,255,0)
BLACK = (0,0,0)
BACKGROUND = (25,25,25)

imgpathdict = {
    (PlayerColour.white, ChessmanName.pawn): RESOURCEPATH/'chessman/white_pawn.png',
    (PlayerColour.white, ChessmanName.rook): RESOURCEPATH/'chessman/white_rook.png',
    (PlayerColour.white, ChessmanName.knight): RESOURCEPATH/'chessman/white_knight.png',
    (PlayerColour.white, ChessmanName.bishop): RESOURCEPATH/'chessman/white_bishop.png',
    (PlayerColour.white, ChessmanName.king): RESOURCEPATH/'chessman/white_king.png',
    (PlayerColour.white, ChessmanName.queen): RESOURCEPATH/'chessman/white_queen.png',
    (PlayerColour.black, ChessmanName.pawn): RESOURCEPATH/'chessman/black_pawn.png',
    (PlayerColour.black, ChessmanName.rook): RESOURCEPATH/'chessman/black_rook.png',
    (PlayerColour.black, ChessmanName.knight): RESOURCEPATH/'chessman/black_knight.png',
    (PlayerColour.black, ChessmanName.bishop): RESOURCEPATH/'chessman/black_bishop.png',
    (PlayerColour.black, ChessmanName.king): RESOURCEPATH/'chessman/black_king.png',
    (PlayerColour.black, ChessmanName.queen): RESOURCEPATH/'chessman/black_queen.png',
}

class PygameInterface:
    TILE_COLOURS  = DARK, MID, LITE
    GAME_SIZE = 600, 600
    SCREEN_SIZE = 600, 620
    SIZE = 30,30
    IMG_SIZE = 45, 45
    ORIGIN = 300,300

    def __init__(self, game=None):
        self.layout = Layout(ORIENTATIONS['flat'], Point(*self.SIZE), Point(*self.ORIGIN))
        self._imglib = {}
        self.done = False
        if game is None:
            game = Game()
        self.game = game
        self.active = None
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        pygame.font.init()
        self.font = pygame.font.SysFont('Calibri',14)
    def _get_image(self, imgpath):
        img = self._imglib.get(imgpath)
        if img is None:
            img = Image.open(imgpath).resize(self.IMG_SIZE).convert('RGBA')
            self._imglib[imgpath] = img = pygame.image.frombuffer(img.tobytes(), img.size, img.mode)
        return img
    def draw_board(self):
        for tile, colour in self.game.board.colours.items():
            self.draw_hex(tile, self.TILE_COLOURS[colour])
            ## add column letters
            if tile.row==1:
                points = tile.vertices(self.layout)
                l, r, b = min(p.x for p in points), max(p.x for p in points), max(p.y for p in points)
                x = (l+r)/2
                y = b+self.SIZE[1]/6
                t = self.font.render(tile.col, False, WHITE)
                self.screen.blit(t, (x, y))
            if tile.col=='a' or tile.notation in ['b7','c8','d9','e10','f11']:
                points = tile.vertices(self.layout)
                l, t = min(p.x for p in points), min(p.y for p in points)
                x = l-self.SIZE[0]/6
                y = t+self.SIZE[0]/8
                t = self.font.render(f"{tile.row:2d}", False, WHITE)
                self.screen.blit(t, (x, y))
    def draw_hex(self, hex, colour, alpha=256):
        vertices = hex.vertices(self.layout)
        surface_size = (max(p.x for p in vertices), max(p.y for p in vertices))
        surface = pygame.Surface(surface_size)
        surface.set_colorkey((0,0,0))
        surface.set_alpha(alpha)
        pygame.draw.polygon(surface, colour, vertices)
        self.screen.blit(surface, (0,0))# hex.to_pixel(self.layout))
    def draw_piece(self, colour, name, position):
        image = self._get_image(imgpathdict[colour, name])
        self.screen.blit(image, position)
    def draw_pieces(self):
        for tile, piece in self.game.board.pieces.items():
            if piece is None: continue
            vertices = tile.vertices(self.layout)
            offsetx, offsety = self.IMG_SIZE[0]/6, self.IMG_SIZE[1]/6
            position = min(p.x for p in vertices)+offsetx, min(p.y for p in vertices)+offsety
            self.draw_piece(piece.colour, piece.name, position)
    def promotion_dialog(self):
        ### PROMOTION GUI
        PROMOTION_PIECES = ChessmanName.knight,ChessmanName.bishop,ChessmanName.rook,ChessmanName.queen
        PROMOTION_GUI_ORIGIN = self.GAME_SIZE[0]/2, self.GAME_SIZE[1]/2
        PROMOTION_GUI_PAD = 5
        PROMOTION_GUI_SIZE = self.IMG_SIZE[0]*4+PROMOTION_GUI_PAD*5, self.IMG_SIZE[1]+PROMOTION_GUI_PAD*2
        l, t, w, h = (
            PROMOTION_GUI_ORIGIN[0] - PROMOTION_GUI_SIZE[0]//2,
            PROMOTION_GUI_ORIGIN[1] - PROMOTION_GUI_SIZE[1]//2,
            PROMOTION_GUI_SIZE[0],
            PROMOTION_GUI_SIZE[1]
        )
        PROMOTION_PIECE_LOCS = [(l+i*(PROMOTION_GUI_PAD+self.IMG_SIZE[0])+PROMOTION_GUI_PAD, t) for i in range(4)]

        pieces = [(self.game.turn_colour, piece) for piece in PROMOTION_PIECES]
        pygame.draw.rect(self.screen, BLUE, (l,t,w,h), 0)
        for (colour, piece), loc in zip(pieces, PROMOTION_PIECE_LOCS):
            self.draw_piece(colour, piece, loc)
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = pygame.mouse.get_pos()
                    if l<x<(l+w) and t<y<(t+h):
                        for piece, (edge,_) in zip(pieces, PROMOTION_PIECE_LOCS[1:]):
                            if x < edge: return piece
                        else: return pieces[-1]
    def board_interaction(self, tile):
        if tile not in self.game.board.pieces: return
        piece = self.game.board.pieces[tile]
        if self.active is None:
            if piece is not None and piece.colour is self.game.turn_colour:
                self.active = tile
        else:
            active_piece = self.game.board.pieces[self.active]
            for move in active_piece.moves:
                if move.target == tile:
                    if move.promote:
                        colour, name = self.promotion_dialog()
                        promote_piece = hex(colour.value+name.value)[-1]
                        move = Move(move.origin, move.target, promote=True, capture=move.capture, promote_piece=promote_piece)
                    self.game.conduct_move(move)
                    self.active = None
                    break
            else:
                if piece is not None and piece.colour is self.game.turn_colour:
                    self.active = tile
        self.flip()
    def parse_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
                return
            if event.type == pygame.MOUSEBUTTONUP:
                self.board_interaction(Hex.from_pixel(Point(*pygame.mouse.get_pos()), self.layout))
            if event.type == pygame.KEYDOWN:
                pressed = pygame.key.get_pressed()
                # if pressed[pygame.K_r]:
                #     winner = opponent[self.turn_col]
                #     print(f'{self.turn_col} resigns. {self.players[winner].name} wins.')
                #     self.end(winner)
                # if pressed[pygame.K_d]:
                #     print('Draw')
                #     self.end('draw')
                # if pressed[pygame.K_p]:
                #     print('Pause')
                #     self.pause()
                # if pressed[pygame.K_h]:
                #     print(self.history)
    def run(self):
        pygame.init()
        self.flip()
        while not self.done:
            self.parse_events()
        pygame.quit()
    def show_moves(self):
        piece = self.game.board.pieces.get(self.active)
        if piece is None: return
        for move in piece.moves:
            if move.promote: colour = BLUE
            elif move.capture: colour = RED
            else: colour = GREEN
            self.draw_hex(move.target, colour, 128)
    def flip(self):
        self.draw_board()
        self.show_moves()
        self.draw_pieces()
        pygame.display.flip()


if __name__ == '__main__':
    # pyg = PygameInterface(Game.load(b'\xb0\x00\t\t\x90\x000\x90\x00\xa0\x90\x91\x10\xb0\xa0\x10\xb0\xc9\x00\x00\x90\x00\x00\x00\x00\x00@\x00\x00\x00\x03\x12A\x1eb\xc0\x00\x00\x90\r\x10\x01\x05\x010\x00J\x17\x00\x81\x82\x00\x17\x93\x00'))
    pyg = PygameInterface()
    pyg.game.conduct_move(Move.from_notation('e5', pyg.game))
    pyg.run()
    print(pyg.game.dump())