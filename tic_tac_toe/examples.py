from game import Game
from ai import AI

g = Game()
g.make_move(1, 1)
g.make_move(0, 0)
g.get_valid_moves()
g.make_move(1, 0)
g.make_move(0, 1)

g.find_best_move()

g.make_move(2, 2)
g.make_move(0, 2)
g._board.print()

ai = AI()
