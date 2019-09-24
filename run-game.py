import enum
import random
from typing import Tuple, List

class Tile():
    pass


class TilePower(int, Tile):
    """1 to 11"""
    def __new__(cls, x):
        if not 1 <= x <= 11:
            raise Exception(f"Needs to be 1 <= x <= 11 but is {x}")
        return int.__new__(cls, x)

    def __str__(self):
        return str(2**self)

class _BlankTile(Tile):
    def __str__(self):
        return " "

BLANK_TILE = _BlankTile()

class Board(tuple):

    HEIGHT = WIDTH = 4

    def __new__(cls, x: Tuple[Tuple[Tile]]):
        """TODO: make not require tuple grid"""
        if len(x) != cls.HEIGHT:
            raise Exception(f"Height needs to be {cls.HEIGHT} but is {len(x)}.")
        for row in x:
            if len(row) != cls.WIDTH:
                raise Exception(f"Width needs to be {cls.WIDTH} but is {len(row)}.")
        return super().__new__(cls, x)

    def __str__(self):
        rows = (" | ".join(str(x) for x in row) for row in self)
        return "\n".join(rows)


class Transformation():
    pass

class SpawnerTransformation(Transformation):
    CHANCE_OF_4_SPAWN = 0.2

    def __get_blank_locations(self, board: Board) -> List[Tuple[int]]:
        return [(j, i) for j, row in enumerate(board)
                for i, tile in enumerate(row)
                if tile == BLANK_TILE]

    def __get_new_tile(self):
        if random.random() < self.CHANCE_OF_4_SPAWN:
            return TilePower(2)
        return TilePower(1)

    def transform(self, board: Board) -> Board:
        spawn_j, spawn_i = random.choice(self.__get_blank_locations(board))
        tmp_board = list(list(row) for row in board)
        tmp_board[spawn_j][spawn_i] = self.__get_new_tile()

        return Board(tmp_board)


class LeftTransform(Transformation):
    """User presses left button"""

    def transform(self, board: Board) -> Board:
        def transform_row(row):
            nonblank_tiles = [x for x in row if x != BLANK_TILE]
            i, new_row = 0, []
            while i < len(nonblank_tiles):
                curr_tile = nonblank_tiles[i]
                to_merge = i != len(nonblank_tiles) - 1 and curr_tile == nonblank_tiles[i+1]
                if to_merge:
                    new_row.append(TilePower(curr_tile + 1))
                    i += 2
                else:
                    new_row.append(curr_tile)
                    i += 1
            new_row += [BLANK_TILE] * (len(row) - len(new_row))
            return new_row
        return Board([transform_row(row) for row in board])


leftTransform = LeftTransform()

EMPTY_BOARD = Board([[BLANK_TILE] * Board.HEIGHT] * Board.WIDTH)
row = (TilePower(1), TilePower(1), TilePower(3), TilePower(4))
some_board = Board([row] * 4)

spawnerTrans = SpawnerTransformation()

if __name__ == "__main__":
    curr_board = EMPTY_BOARD
    print(leftTransform.transform(some_board))