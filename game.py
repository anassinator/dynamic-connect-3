#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from board import SmallBoard
from base_board import Board, Player
from draw_tracker import DrawTracker
from move import Move, Direction, InvalidMove

class Game(object):

    """A game instance.
    
    Attributes:
        board: Current board state.
        turn: Current player.
        won: Which player won.
        draw: Whether the game ended in a draw or not.
    """

    def __init__(self, board: Board, draw_tracker: DrawTracker=None):
        """Constructs a Game instance from a given starting position.
        
        Args:
            board: Starting board position.
            draw_tracker: Draw tracker to start with.
        """
        self.board = board
        self.turn = Player.white
        self.won = Player.none
        self.draw = False

        if draw_tracker is None:
            self._draw_tracker = DrawTracker()
            self._draw_tracker.update(self.board, self.turn)
        else:
            self._draw_tracker = draw_tracker

    def play(self, move: Move):
        """Plays a given move and switches to next player's turn.
        
        Args:
            move: Move to play.
        """
        # Make sure it's the correct person's move.
        # Empty cells raise an InvalidMove in self.board.move so deal with it
        # there.
        if self.board.get(move.x, move.y) not in (self.turn, Player.none):
            raise InvalidMove("Not your turn")

        self.board.move(move)
        if self.board.is_goal(self.turn):
            self.won = self.turn

        self.turn = Player(not self.turn.value)
        self.draw = self._draw_tracker.update(self.board, self.turn)

    def copy(self) -> "Game":
        """Returns a deep copy of the game.

        Returns:
            A copy of the current game state.
        """
        game = Game(self.board.copy(), self._draw_tracker.copy())
        game.turn = self.turn
        game.won = self.won
        game.draw = self.draw
        return game


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

        if game.won != Player.none:
            print("{} wins.".format(game.won.name.capitalize()))
            break

        if game.draw:
            print("Draw.")
            break

