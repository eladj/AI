from copy import deepcopy
from enum import Enum
import numpy as np

BOARD_SIZE = 3
BIT_TYPE = np.uint16


class Piece(Enum):
    X = 0
    O = 1


class Score(Enum):
    Win = 1
    Draw = 0
    Lose = -1


class State:
    """ Represents the TicTacToe board state using BitBoard:
    0 1 2
    3 4 5
    6 7 8

    - First channel used for 'X', second for 'O'
    For example, putting an 'X' at 4 is: 'X': 0000 0000 0001 0000
    """
    def __init__(self):
        self.bits = np.zeros(2, dtype=BIT_TYPE)
        self.current_piece_turn = Piece.X
        self.is_game_on = True
        self.score = None
        self._valid_bitmask = 0b000000111111111  # Only the first 9-bits are valid

    def set_square(self, ind: int, piece: Piece):
        bb_tile = self._ind_to_bit(ind)
        if self.bits[piece.value] & bb_tile:
            raise RuntimeError("Illegal 'set_square': tile {} is occupied".format(ind))
        else:
            self.bits[piece.value] = self.bits[piece.value] | bb_tile

    def do_move(self, move):
        self.set_square(ind=move.ind, piece=move.piece)
        if self.current_piece_turn == Piece.X:
            self.current_piece_turn = Piece.O
        elif self.current_piece_turn == Piece.O:
            self.current_piece_turn = Piece.X

    def is_occupied(self, ind: int) -> bool:
        bb_tile = self._ind_to_bit(ind)
        return (self.bits[Piece.X.value] & bb_tile) | (self.bits[Piece.O.value] & bb_tile)

    def clear(self):
        self.bits = self.bits & 0

    def clear_square(self, ind: int, piece: Piece):
        bb_tile = self._ind_to_bit(ind)
        if ~(self.bits[piece.value] & bb_tile):
            raise RuntimeError("Illegal 'clear_square': tile {} is already empty".format(ind))
        else:
            self.bits[piece.value] = self.bits[piece.value] & (~bb_tile)

    def set_square_2d(self, i: int, j: int, piece: Piece):
        self.set_square(ind=self._ij_to_ind(i, j), piece=piece)

    def is_occupied_2d(self, i: int, j: int) -> bool:
        self.is_occupied(ind=self._ij_to_ind(i, j))

    def clear_square_2d(self, i: int, j: int, piece: Piece):
        self.clear_square(ind=self._ij_to_ind(i, j), piece=piece)

    @staticmethod
    def _ind_to_bit(ind: int) -> BIT_TYPE:
        return BIT_TYPE(2**ind)

    @staticmethod
    def _bit_to_ind(bits: BIT_TYPE) -> int:
        return bits.item().bit_length()

    @staticmethod
    def _ij_to_ind(i: int, j: int) -> int:
        return np.ravel_multi_index((i, j), (BOARD_SIZE, BOARD_SIZE))

    @staticmethod
    def _bit_to_ij(bits: BIT_TYPE) -> (int, int):
        return np.unravel_index(bits.item().bit_length(), (BOARD_SIZE, BOARD_SIZE))

    def print_board(self):
        s = ""
        for ind in range(BOARD_SIZE*BOARD_SIZE):
            if self.bits[Piece.X.value] & self._ind_to_bit(ind):
                s += "X"
            elif self.bits[Piece.O.value] & self._ind_to_bit(ind):
                s += "O"
            else:
                s += "·"
            if (ind + 1) % BOARD_SIZE == 0:
                s += "\n"
        print(s)

    def is_draw(self) -> bool:
        draw_state = 0b000000111111111  # All tiles are full
        if ((self.bits[Piece.X.value] | self.bits[Piece.O.value]) & draw_state) == draw_state:
            return True
        else:
            return False

    def has_ended(self) -> (bool, Score):
        win_states = (
            0b0000000000000111,
            0b0000000000111000,
            0b0000000111000000,
            0b0000000100100100,
            0b0000000010010010,
            0b0000000001001001,
            0b0000000100010001,
            0b0000000001010100)

        # First check for win state
        for win_state in win_states:
            if self.bits[Piece.X.value] & win_state == win_state:
                return True, Score.Win
            elif self.bits[Piece.O.value] & win_state == win_state:
                return True, Score.Lose
        # If no one won, check for draw
        if self.is_draw():
            return True, Score.Draw
        return False, None

    def open_tiles(self):
        open_tiles_bits = (~(self.bits[Piece.X.value] | self.bits[Piece.O.value])) & self._valid_bitmask
        open_tiles_indices = [n for n in range(BOARD_SIZE*BOARD_SIZE) if ((open_tiles_bits >> n) & 0x0001)]
        return open_tiles_indices


class Move:
    def __init__(self, ind: int, piece: Piece):
        self.ind = ind
        self.piece = piece
        self.row, self.col = np.unravel_index(self.ind, (BOARD_SIZE, BOARD_SIZE))

    def __repr__(self):
        def col_to_letter(col: int):
            return chr(col + ord('A'))
        return "<Move: {}{}{}>".format(self.piece.name, col_to_letter(self.col), self.row)


class Game:
    def __init__(self):
        self.state = State()
        self.reset()

    def reset(self):
        self.state.clear()

    def play_turn(self, move: Move):
        self.check_move_valid(move)
        self.state.set_square(move.ind, move.piece)
        has_ended, score = self.state.has_ended()
        if has_ended:
            self.state.is_game_on = False
            self.state.score = score
            print("Game Ended: {} !".format(score.name))
        else:
            self._advance_turn()

    def check_move_valid(self, move: Move):
        if move.row < 0 or move.row >= BOARD_SIZE or move.col < 0 or move.col >= BOARD_SIZE:
            raise RuntimeError("Move not valid: out of bounds")
        if move.piece != self.state.current_piece_turn:
            raise RuntimeError("Move not valid: wrong player to move")
        if self.state.is_occupied(move.ind):
            raise RuntimeError("Move not valid: tile already occupied")
        if self.state.current_piece_turn != move.piece:
            raise RuntimeError("Move not valid: That's not {} turn".format(move.piece.name))
        if not self.state.is_game_on:
            raise RuntimeError("Move not valid: game has ended")

    def _advance_turn(self):
        if self.state.current_piece_turn == Piece.X:
            self.state.current_piece_turn = Piece.O
        elif self.state.current_piece_turn == Piece.O:
            self.state.current_piece_turn = Piece.X


def minimax(state: State, maximizing_player: bool=True):
    has_ended, score = state.has_ended()
    if has_ended:
        return None, score.value  # +1 for win, -1 for loss, 0 for draw

    moves_list = [Move(i, piece=state.current_piece_turn) for i in state.open_tiles()]
    best_move = None
    if maximizing_player:  # Maximizing player
        value = -float('inf')
        for move in moves_list:
            new_state = deepcopy(state)
            new_state.do_move(move)
            _, cur_value = minimax(new_state, maximizing_player=False)
            if cur_value > value:
                value = cur_value
                best_move = move
    else:  # Minimizing player
        value = float('inf')
        for move in moves_list:
            new_state = deepcopy(state)
            new_state.do_move(move)
            _, cur_value = minimax(new_state, maximizing_player=True)
            if cur_value < value:
                value = cur_value
                best_move = move
    return best_move, value


if __name__ == "__main__":
    game = Game()
    game.play_turn(Move(1, game.state.current_piece_turn))
    game.play_turn(Move(0, game.state.current_piece_turn))
    game.play_turn(Move(3, game.state.current_piece_turn))
    game.play_turn(Move(7, game.state.current_piece_turn))
    game.play_turn(Move(6, game.state.current_piece_turn))
    # game.play_turn(Move(5, game.state.current_piece_turn))
    # game.play_turn(Move(5, game.state.current_piece_turn))
    # game.play_turn(Move(8, game.state.current_piece_turn))
    game.state.print_board()
    print(game.state.open_tiles())
    print(minimax(game.state, maximizing_player=game.state.current_piece_turn==Piece.X))
