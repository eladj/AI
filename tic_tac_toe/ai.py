import sys
sys.path.insert(0, '/Users/ejoseph/code_private/AI')
import ai
from game import Game


class AI:
    def __init__(self):
        pass

    def build_game_tree(self, depth=-1):
        node = ai.Node()
