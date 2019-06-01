from copy import deepcopy
from enum import Enum
import numpy as np

BOARD_SIZE = 3


class Piece(Enum):
    X = 0
    O = 1


class Tile(Enum):
    X = Piece.X.value
    O = Piece.O.value
    Empty = 2


class Score(Enum):
    Win = 1  # 'X' won
    Draw = 0
    Lose = -1  # 'O' won


class GameState(Enum):
    Playing = 0
    Finished = 1


class Player:
    ID = 0

    def __init__(self, piece: Piece, name=None):
        self._name = name
        self._piece = piece
        self.num_wins = 0
        self.num_loses = 0
        self.num_draws = 0
        self._id = deepcopy(Player.ID)
        if name is None:
            self._name = "P{}".format(self._id)
        Player.ID += 1

    @property
    def name(self):
        return self._name

    @property
    def piece(self):
        return self._piece


class Board:
    def __init__(self, rows=3, cols=3):
        self._rows = rows
        self._cols = cols
        self._board = np.ones((self.rows, self.cols), dtype=np.uint8)
        self.reset()

    def reset(self):
        self._board = np.ones((self.rows, self.cols), dtype=np.uint8) * Tile.Empty.value

    def get_tile(self, x, y) -> Tile:
        if x > self.cols or y > self.rows or x < 0 or y < 0:
            raise RuntimeError("Tile out of bounds")
        return Tile(self.board[y, x])

    def set_tile(self, x, y, piece: Piece):
        if x > self.cols or y > self.rows or x < 0 or y < 0:
            raise RuntimeError("Tile out of bounds")
        self._board[y, x] = piece.value

    def print(self, with_grid=True):
        s = ""
        if with_grid:
            s += " " + "".join([str(x) for x in range(self.cols)]) + "\n"
        for y in range(self.rows):
            if with_grid:
                s += "{}".format(y)
            for x in range(self.cols):
                tile = self.get_tile(x, y)
                if tile == Tile.Empty:
                    s += "·"
                else:
                    s += self.get_tile(x, y).name
            s += "\n"
        print(s)

    @property
    def rows(self):
        return self._rows

    @property
    def cols(self):
        return self._cols

    @property
    def board(self):
        return self._board


class Game:
    def __init__(self):
        self._board = Board(rows=3, cols=3)
        self._game_state = GameState.Finished
        self.players = [Player(piece=Piece.X), Player(piece=Piece.O)]
        self.player_ind_to_move = 0
        self._score = Score.Draw
        self.reset()

    def reset(self):
        self._board.reset()
        self._game_state = GameState.Playing
        self.player_ind_to_move = 0
        print("Player {} turn".format(self.player_to_move.piece.name))

    def make_move(self, x, y):
        # Check that we are playing
        if self._game_state != GameState.Playing:
            raise RuntimeError("GameState is not GameState.Playing")

        # Check if move is valid
        if self._board.get_tile(x, y) != Tile.Empty:
            raise RuntimeError("Tile Not Empty")

        # Put new marker
        self._board.set_tile(x, y, self.player_to_move.piece)

        # Check if current player won
        if self.is_win(self.player_to_move.piece):
            if self.player_to_move.piece.X:
                self._score = Score.Win
            else:
                self._score = Score.Lose
            print("Player {} won!".format(self.player_to_move.piece.name))
            self._game_state = GameState.Finished
            return

        # Check if draw
        if self.is_draw():
            self._score = Score.Draw
            print("Draw")
            self._game_state = GameState.Finished
            return

        # Change the next player to move
        self.player_ind_to_move = (self.player_ind_to_move + 1) % 2
        print("Player {} turn".format(self.player_to_move.piece.name))

    def is_win(self, piece: Piece) -> bool:
        b = self._board.board == piece.value  # True in each tile of the given piece
        rows_win = np.any(np.all(b, axis=0))
        cols_win = np.any(np.all(b, axis=1))
        diag1_win = np.all(np.diag(b))
        diag2_win = np.all(np.diag(np.fliplr(b)))
        if rows_win or cols_win or diag1_win or diag2_win:
            return True
        return False

    def is_draw(self) -> bool:
        # Assuming that we already checked for a win
        b = self._board.board == Tile.Empty.value  # True in each empty tile
        if not(np.any(b)):
            return True
        return False

    def get_valid_moves(self):
        """ Gives an array of x and y empty tiles """
        b = self._board.board == Tile.Empty.value  # True in each empty tile
        y, x = np.nonzero(b)
        return x, y

    @property
    def player_to_move(self):
        return self.players[self.player_ind_to_move]

    @property
    def score(self):
        return self._score


if __name__ == "__main__":
    g = Game()
    g.make_move(1, 1)
    g.make_move(0, 0)
    g.get_valid_moves()
    g.make_move(1, 0)
    g.make_move(0, 1)
    g.make_move(2, 2)
    g.make_move(0, 2)
    g._board.print()

