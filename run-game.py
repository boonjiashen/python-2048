import enum
import random
import keyboard
import sys
from typing import Tuple, List

class Tile():
    pass


class TilePower(int, Tile):
    """1 to 11"""
    MIN_POWER = 1
    MAX_POWER = 11

    def __new__(cls, x):
        if not cls.MIN_POWER <= x <= cls.MAX_POWER:
            raise Exception(f"Needs to be {cls.MIN_POWER} <= x <= {cls.MAX_POWER} but is {x}")
        return int.__new__(cls, x)

    def __str__(self):
        return str(2**self)


class _BlankTile(str, Tile):
    pass


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

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        """True if value of each tile is the same"""
        def is_tile_eq(x, y):
            if x == BLANK_TILE and y == BLANK_TILE:
                return True
            if x != BLANK_TILE and y != BLANK_TILE:
                return x == y
            return False
        self_tiles = [x for row in self for x in row]
        other_tiles = [x for row in other for x in row]
        return all(x == y for x, y in zip(self_tiles, other_tiles))


class Transformation():
    pass

class SpawnTransform(Transformation):
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


def flipLeftRight(board: Board) -> Board:
    return Board([row[::-1] for row in board])


def transpose(board: Board) -> Board:
    return Board(list(zip(*[row for row in board])))


class RightTransform(Transformation):
    """User presses right button"""

    def transform(self, board: Board) -> Board:
        board = flipLeftRight(board)
        board = LeftTransform().transform(board)
        board = flipLeftRight(board)

        return board


class UpTransform(Transformation):
    """User presses up button"""

    def transform(self, board: Board) -> Board:
        board = transpose(board)
        board = LeftTransform().transform(board)
        board = transpose(board)

        return board


class DownTransform(Transformation):
    """User presses down button"""

    def transform(self, board: Board) -> Board:
        board = flipLeftRight(transpose(board))
        board = LeftTransform().transform(board)
        board = transpose(flipLeftRight(board))

        return board


class Direction(enum.Enum):
    UP = enum.auto()
    DOWN = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()


class Game():
    def __init__(self,
                 initialState,
                 spawnTransform=SpawnTransform(),
                 leftTransform=LeftTransform(),
                 rightTransform=RightTransform(),
                 upTransform=UpTransform(),
                 downTransform=DownTransform(),
                 ):
        self._board = initialState
        self._spawnTransform = spawnTransform
        self._upTransform = upTransform
        self._downTransform = downTransform
        self._leftTransform = leftTransform
        self._rightTransform = rightTransform

    def get_curr_state(self) -> Board:
        return self._board

    def has_succeeded(self) -> bool:
        return any(x == TilePower(TilePower.MAX_POWER)
                   for row in self._board
                   for x in row)

    def has_failed(self) -> bool:
        return not any(x == BLANK_TILE
                       for row in self._board
                       for x in row)

    def has_ended(self) -> bool:
        return self.has_succeeded() or self.has_failed()

    def swipe(self, direction: Direction) -> None:
        if self.has_ended():
            raise Exception("Game has already ended")
        transforms = {
            Direction.UP: self._upTransform,
            Direction.DOWN: self._downTransform,
            Direction.LEFT: self._leftTransform,
            Direction.RIGHT: self._rightTransform,
        }
        next_board = transforms[direction].transform(self._board)
        if next_board != self._board:
            self._board = self._spawnTransform.transform(next_board)


def generate_random_board() -> Board:
    def generate_random_tile() -> Tile:
        if random.random() < 0.5:
            return BLANK_TILE
        return TilePower(random.randint(TilePower.MIN_POWER, TilePower.MAX_POWER))
    return Board(tuple(tuple(generate_random_tile() for _ in range(Board.WIDTH))
                       for _ in range(Board.HEIGHT)))


def display(board: Board) -> None:
    rows = (" | ".join([""] + [f"{str(x):>4}" for x in row] + [""]) for row in board)
    ruler = " " + "-" * 29 + " "
    print(ruler)
    for row in rows:
        print(row)
    print(ruler)


def run_game():
    EMPTY_BOARD = Board([[BLANK_TILE] * Board.HEIGHT] * Board.WIDTH)
    initial_state = SpawnTransform().transform(EMPTY_BOARD)
    game = Game(initial_state)

    def on_arrow_keypress(event):
        directions = {
            "up": Direction.UP,
            "down": Direction.DOWN,
            "left": Direction.LEFT,
            "right": Direction.RIGHT,
        }
        if event.name not in directions:
            return

        game.swipe(directions[event.name])
        print()
        print()
        display(game.get_curr_state())

        if game.has_ended():
            print("Game has ended!")
            if game.has_succeeded():
                print("You won!")
            if game.has_failed:
                print("You lost! Try again next time!")
            sys.exit()

    keyboard.on_press(on_arrow_keypress)
    display(game.get_curr_state())
    while True:
        pass


if __name__ == "__main__":
    run_game()