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
        if len(x) != cls.HEIGHT:
            raise Exception(f"Height needs to be {cls.HEIGHT} but is {len(x)}")
        if any(len(row) != cls.WIDTH for row in x):
            raise Exception(f"Width not ${cls.WIDTH}")
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

EMPTY_BOARD = Board([[BLANK_TILE] * Board.HEIGHT] * Board.WIDTH)
row = (TilePower(1), BLANK_TILE, TilePower(3), TilePower(4))
some_board = Board([row] * 4)

spawnerTrans = SpawnerTransformation()

if __name__ == "__main__":
    curr_board = EMPTY_BOARD
    print(curr_board, "\n")
    for _ in range(5):
        curr_board = spawnerTrans.transform(curr_board)
        print(curr_board, "\n")