from game import Game, Move, Piece
from ai import AI

g = Game()
g.make_move(Move(1, 1, Piece.X))
g.make_move(Move(0, 0, Piece.O))
g.make_move(Move(1, 0, Piece.X))
g.make_move(Move(0, 1, Piece.O))

g._board.print()
next_move = g.find_best_move()
g.make_move(next_move)

g._board.print()
next_move = g.find_best_move()
g.make_move(next_move)

g._board.print()
next_move = g.find_best_move()
g.make_move(next_move)

g._board.print()

# g.make_move(0, 0)
# g.make_move(0, 2)
# g.make_move(2, 0)
# g.make_move(1, 0)
# g.find_best_move()
