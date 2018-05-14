
from __future__ import print_function

from game import board, game

class player(object):
    def __init__(self):
        self.player = None
    
    def get_action(self, board):
        try:
            action = raw_input("Your move: ")
            if action == 'w' or action == "W":
                board.moveUp()
            elif action == 'a' or action == "A":
                board.moveLeft()
            elif action == 's' or action == "S":
                board.moveDown()
            elif action == 'd' or action == "D":
                board.moveRight()
        except Exception:
            move = -1
        if move == -1:
            print("invalid move")
            move = self.get_action(board)
        return move


def run():
    try:
        b = board()
        g = game(b)
        p = player()
        g.start_play(p,is_shown=1)
    except KeyboardInterrupt:
        print('\n\rquit')

if __name__ == '__main__':
    run()