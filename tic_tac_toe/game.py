from copy import deepcopy
from enum import Enum
import numpy as np


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

    def __init__(self, piece: Piece, name=None, is_ai=False):
        self._name = name
        self._piece = piece
        self._is_ai = is_ai
        self._id = deepcopy(Player.ID)
        if name is None:
            self._name = "P{}".format(self._id)
        Player.ID += 1

    @property
    def name(self):
        return self._name

    @property
    def is_ai(self):
        return self._is_ai

    @property
    def piece(self):
        return self._piece


class Move:
    def __init__(self, x: int, y: int, piece: Piece):
        self.x = x
        self.y = y
        self.piece = piece


class Board:
    def __init__(self, rows=3, cols=3):
        self._board = np.ones((rows, cols), dtype=np.uint8)
        self.reset()

    def reset(self):
        self._board = np.ones((self.rows, self.cols), dtype=np.uint8) * Tile.Empty.value

    def get_tile(self, x, y) -> Tile:
        if x > self.cols or y > self.rows or x < 0 or y < 0:
            raise RuntimeError("Tile out of bounds")
        return Tile(self.board[y, x])

    def set_tile(self, move: Move):
        if move.x > self.cols or move.y > self.rows or move.x < 0 or move.y < 0:
            raise RuntimeError("Tile out of bounds")
        self._board[move.y, move.x] = move.piece.value

    def print(self, with_grid=False):
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
        return self._board.shape[0]

    @property
    def cols(self):
        return self._board.shape[1]

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
        self._move_list = []
        self.reset()

    def reset(self):
        self._board.reset()
        self._game_state = GameState.Playing
        self.player_ind_to_move = 0
        print("Player {} turn".format(self.player_to_move.piece.name))

    def make_move(self, move: Move, verbose=False):
        # Check that we are playing
        if self._game_state != GameState.Playing:
            raise RuntimeError("GameState is not GameState.Playing")

        # Check if move is valid
        if self._board.get_tile(move.x, move.y) != Tile.Empty:
            raise RuntimeError("Tile Not Empty")
        if move.piece != self.player_to_move.piece:
            raise RuntimeError("It's not {} turn".format(move.piece.name))

        # Put new marker
        self._board.set_tile(move)
        self._move_list.append(move)

        # Check if current player won
        if self.is_win(self.player_to_move.piece):
            if self.player_to_move.piece == Piece.X:
                self._score = Score.Win
            else:
                self._score = Score.Lose
            if verbose:
                print("Player {} won!".format(self.player_to_move.piece.name))
            self._game_state = GameState.Finished
            return

        # Check if draw
        if self.is_draw():
            self._score = Score.Draw
            if verbose:
                print("Draw")
            self._game_state = GameState.Finished
            return

        # Change the next player to move
        self.player_ind_to_move = (self.player_ind_to_move + 1) % 2
        if verbose:
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

    @staticmethod
    def get_valid_moves_s(board: Board) -> Move:
        b = board == Tile.Empty.value  # True in each empty tile
        y, x = np.nonzero(b)
        return x, y

    def find_best_move(self, game_obj=None, node=None, depth=9):
        if game_obj is None:
            game_obj = self
        if node is None:
            root = Node(value=0)
            root.state = deepcopy(self._board)

        # Recursively expand the game tree
        valid_moves_x, valid_moves_y = game_obj.get_valid_moves()
        for move_ind in range(len(valid_moves_x)):
            # Create a separate version of the game
            game_copy = deepcopy(game_obj)
            # Make the move
            game_copy.make_move(Move(x=valid_moves_x[move_ind], y=valid_moves_y[move_ind], piece=game_copy.player_to_move.piece))
            if node is None:
                # Add a node to the tree with this move ans score
                child = root.add_child(Node(value=game_copy.score.value, state=game_copy._board))
            else:
                child = node.add_child(Node(value=game_copy.score.value, state=game_copy._board))
            # If the game is still on-going, continue with this branch
            if game_copy._game_state == GameState.Playing and depth > 0:
                self.find_best_move(game_obj=game_copy, node=child, depth=depth-1)
        if node is None:
            # We came back to the initial call to the function and we populate the values
            # of each node using minimax algorithm
            minimax(node=root, depth=depth)
            # We select the child with the best score
            best_move_ind = np.argmax([x.value for x in root.children])
            move = Move(x=valid_moves_x[best_move_ind], y=valid_moves_y[best_move_ind], piece=self.player_to_move.piece)
            return move

    @property
    def player_to_move(self):
        return self.players[self.player_ind_to_move]

    @property
    def score(self):
        return self._score


class Node:
    def __init__(self, value=0, state=None):
        self.value = value
        self.state = state
        self.parent = None
        self.children = []

    def add_child(self, node):
        node.parent = self
        self.children.append(node)
        return node

    def is_terminal(self):
        return len(self.children) == 0


def minimax(node: Node, depth: int, maximizing_player: bool = True):
    if depth == 0 or node.is_terminal():
        return node  # the heuristic value of node
    if maximizing_player:
        node.value = -float('inf')
        for child in node.children:
            next_node = minimax(child, depth=depth-1, maximizing_player=False)
            if next_node.value > node.value:
                node.value = next_node.value
    else:  # minimizing player
        node.value = float('inf')
        for child in node.children:
            next_node = minimax(child, depth=depth - 1, maximizing_player=True)
            if next_node.value < node.value:
                node.value = next_node.value
    return node
