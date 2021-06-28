import math
from collections import namedtuple
from itertools import product

Orientation = namedtuple("Orientation", ["forward", "backward", "start_angle"])
Layout = namedtuple("Layout", ["orientation", "size", "origin"])
Point = namedtuple("Point", ["x", "y"])

ORIENTATIONS = {
    'pointy': Orientation(
        forward=[math.sqrt(3.0), math.sqrt(3.0) / 2.0, 0.0, 3.0 / 2.0],
        backward=[math.sqrt(3.0) / 3.0, -1.0 / 3.0, 0.0, 2.0 / 3.0],
        start_angle=0.5
    ),
    'flat': Orientation(
        forward=[3.0 / 2.0, 0.0, math.sqrt(3.0) / 2.0, math.sqrt(3.0)], 
        backward=[2.0 / 3.0, 0.0, -1.0 / 3.0, math.sqrt(3.0) / 3.0], 
        start_angle=0.0
    ),
    'flat_ascii': Orientation(
        forward=[4, 0, 1, 2], 
        backward=[0, 0, 0, 0], # undefined 
        start_angle=0.0
    )
}

def get_radially_symmetric_hexagonal_board(radius): 
    return {Hex(*coords) for coords in product(range(-radius, radius+1), repeat=3) if sum(coords)==0}

class Hex():
    #https://www.redblobgames.com/grids/hexagons/implementation.html
    #most design choices borrowed from ^
    def __repr__(self):
        # return f"Hex(x={self.x}, y={self.y}, z={self.z})"
        return self.notation
    def __init__(self,x,y,z=None):
        self.x = x
        self.y = y
        self.z = -x - y
        if z is not None:
            #TODO: replace with ValueError
            assert z == self.z
    def __lt__(self, other):
        return self.x < other.x and self.y < other.y
    def __hash__(self):
        return hash(self.axial)
    def __eq__(self, compare_hex):
        return self.x == compare_hex.x and self.y == compare_hex.y
    def __ne__(self, compare_hex):
        return not self.__eq__(compare_hex)
    def __add__(self, dv):
        if isinstance(dv, Hex):
            return Hex(self.x + dv.x, self.y + dv.y)
        elif len(dv) == 2:
            return Hex(self.x + dv[0],self.y + dv[1])
    def __sub__(self, dv):
        if isinstance(dv, Hex):
            return Hex(self.x - dv.x, self.y - dv.y)
        elif len(dv, 2):
            return Hex(self.x - dv[0],self.y - dv[1])
    def hex(self):
        return hex(self.x+5)[-1]+hex(self.y+5)[-1]
    @classmethod
    def from_hex(cls, hexstr):
        return cls(int(hexstr[0],16)-5, int(hexstr[1],16)-5)
    def to_pixel(self, layout):
        x = (layout.orientation.forward[0] * self.x + layout.orientation.forward[1] * self.y) * layout.size.x
        y = (layout.orientation.forward[2] * self.x + layout.orientation.forward[3] * self.y) * layout.size.y
        return Point(x + layout.origin.x, y + layout.origin.y)
    def round(self):
        x, y, z = map(int, map(round, (self.x, self.y, self.z)))
        x_diff, y_diff, z_diff = abs(x-self.x), abs(y-self.y), abs(z-self.z)
        if x_diff>y_diff and x_diff>z_diff:
            x = -y-z
        elif y_diff > z_diff:
            y = -x-z
        else:
            z = -x-y
        return Hex(x,y,z)
    @property
    def axial(self):
        return self.x, self.y
    @property
    def cube(self):
        return self.x, self.y, self.z
    @staticmethod
    def from_pixel(point, layout):
        x = (point.x-layout.origin.x)/layout.size.x
        y = (point.y-layout.origin.y)/layout.size.y
        x_ = layout.orientation.backward[0] * x + layout.orientation.backward[1] * y
        y_ = layout.orientation.backward[2] * x + layout.orientation.backward[3] * y
        return Hex(x_, y_).round()
    def vertices(self, layout, offset=True):
        angles = [(math.pi/3) * (layout.orientation.start_angle + i) for i in range(6)]
        if offset:
            x, y = self.to_pixel(layout)
        else:
            x = y = 0
        vertices = [
            Point(
                round(x+layout.size.x*math.cos(angle)), 
                round(y+layout.size.y*math.sin(angle))
            )
            for angle in angles
        ]
        return vertices
    def edges(self, layout):
        vertices = self.vertices(layout)
        vertices_ = vertices[1:] + [vertices[0]]
        return zip(vertices, vertices_)
    def rank(self, direction):
        rank = -self.z if self.x*direction < 0 else self.y
        rank = 6 - direction*rank
        return rank
    @property
    def col(self):
        x = self.x
        if x>3: x+=1
        return chr(102+x)
    @property
    def row(self):
        return 12-self.rank(-1)
    @property
    def notation(self):
        return f"{self.col}{self.row}"
    @classmethod
    def from_notation(cls, notation):
        col, row = notation
        x = ord(col)-102
        if x > 3: x -= 1
        rank = 6-int(row)
        y = rank-x if x>0 else rank
        hex = cls(x, y)
        #TODO: check if this works and remove the assertion
        assert hex.notation == notation
        return hex
hex_directions = set([Hex(1, 0, -1), Hex(1, -1, 0), Hex(0, -1, 1), Hex(-1, 0, 1), Hex(-1, 1, 0), Hex(0, 1, -1)])
hex_diagonals = set([Hex(2, -1, -1), Hex(1, -2, 1), Hex(-1, -1, 2), Hex(-2, 1, 1), Hex(-1, 2, -1), Hex(1, 1, -2)])