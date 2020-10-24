# BSD 2-Clause License

# Copyright (c) 2020, Henry Brausen
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

class Direction:
    NORTH = 0
    SOUTH = 1
    EAST  = 2
    WEST  = 3

    @staticmethod
    def get_opposite(dir):
        return {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST:  Direction.WEST,
            Direction.WEST:  Direction.EAST
        }[dir]

class Tile:
    def __init__(self, values):
        self.values = values

    # Used for printing game state
    def iterlines(self):
        yield f'\\{str(self.values[Direction.NORTH])}/'
        yield f'{str(self.values[Direction.WEST])}.{str(self.values[Direction.EAST])}'
        yield f'/{str(self.values[Direction.SOUTH])}\\'
    
    def matches(self, other, side):
        return self.values[side] == other.values[Direction.get_opposite(side)]
    
    def __hash__(self):
        return hash(tuple(self.values))

class Board:
    def __init__(self, N):
        self.board = [[None for i in range(N)] for j in range(N)]
        self.N = N

    def place_tile(self, tile, row, col):
        self.board[row][col] = tile

    def remove_tile(self, row, col):
        self.board[row][col] = None
    
    def get_neighbours(self, row, col):
        ret = []
        if row > 0 and self.board[row-1][col] is not None:
            ret.append((self.board[row-1][col], Direction.NORTH))
        if row + 1 < self.N and self.board[row+1][col] is not None:
            ret.append((self.board[row+1][col], Direction.SOUTH))
        if col > 0 and self.board[row][col-1] is not None:
            ret.append((self.board[row][col-1], Direction.WEST))
        if col + 1 < self.N and self.board[row][col+1] is not None:
            ret.append((self.board[row][col+1], Direction.EAST))
        return ret
    
    def tile_fits(self, tile, row, col):
        if self.board[row][col] is not None: return False
        neighbours = self.get_neighbours(row, col)
        for nb in neighbours:
            if not tile.matches(*nb):
                return False
        return True

    def __str__(self):
        ret = ''
        def null_generator():
            for i in range(3):
                yield '   '
        for row in self.board:
            generators = []
            for col in row:
                generators.append(col.iterlines() if col else null_generator())
            for i in range(3):
                for g in generators:
                    ret += next(g)
                ret += '\n'
        return ret
 
class GameMove:
    def __init__(self, tile, row, col):
        self.tile = tile
        self.row = row
        self.col = col

class Game:
    def __init__(self, N, tiles):
        self.N = N
        self.tileset = set(tiles)
        self.board = Board(N)
        self.movestack = list()
    
    def get_moves(self):
        moves = []
        # To cut down the search space, we place
        # tiles in a fixed order
        row = (len(self.tileset) - 1) // self.N
        col = (len(self.tileset) - 1) % self.N
        for tile in self.tileset:
            if self.board.tile_fits(tile, row, col):
                moves.append(GameMove(tile, row, col))
        return moves
    
    def make_move(self, move):
        self.movestack.append(move)
        self.board.place_tile(move.tile, move.row, move.col)
        self.tileset.remove(move.tile)
    
    def undo_move(self):
        move_to_undo = self.movestack.pop()
        self.board.remove_tile(move_to_undo.row, move_to_undo.col)
        self.tileset.add(move_to_undo.tile)
    
    def solve(self):
        if not self.tileset:
            print(self.board)
            print('------')
            return

        moves = self.get_moves()
        for move in moves:
            self.make_move(move)
            self.solve()
            self.undo_move()

if __name__ == '__main__':

    # Solve demo problem
    tiles = [
        # N S E W
        Tile([ 2, 6, 2, 5 ]),
        Tile([ 9, 6, 4, 3 ]),
        Tile([ 3, 7, 3, 8 ]),
        Tile([ 5, 9, 3, 3 ]),
        Tile([ 4, 5, 4, 5 ]),
        Tile([ 5, 6, 5, 7 ]),
        Tile([ 8, 4, 7, 2 ]),
        Tile([ 6, 9, 4, 4 ]),
        Tile([ 6, 3, 5, 6 ])
    ]

    g = Game(3, tiles)
    g.solve()
