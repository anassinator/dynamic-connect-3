#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from board import Board, SmallBoard, Player
from move import Move, Direction, InvalidMove

class Game(object):

    """A game instance.
    
    Attributes:
        board: Current board state.
        turn: Current player.
    """

    def __init__(self, board: Board):
        """Constructs a Game instance from a given starting position.
        
        Args:
            board: Starting board position.
        """
        self.board = board
        self.turn = Player.white

    def play(self, move: Move):
        """Plays a given move and switches to next player's turn.
        
        Args:
            move: Move to play.
        """
        if self.board.get(move.x, move.y) == 1 - self.turn.value:
            raise InvalidMove("Not your turn")

        self.board.move(move)
        self.turn = Player(not self.turn.value)


if __name__ == "__main__":
    board = SmallBoard()
    game = Game(board)
    print(game.board)

    while True:
        try:
            s = "{}'s turn. Enter a move: ".format(game.turn.name.capitalize())
            move = Move.from_str(input(s))
            game.play(move)
            print(game.board)
        except InvalidMove as e:
            print(e.message)
        except (KeyboardInterrupt, EOFError):
            break
