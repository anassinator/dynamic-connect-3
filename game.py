#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from move import InvalidMove
from base_board import Player
from draw_tracker import DrawTracker


class Game(object):

    """A game instance.

    Attributes:
        board: Current board state.
        draw: Whether the game ended in a draw or not.
        turn: Current player.
        won: Which player won.
    """

    def __init__(self, board, draw_tracker=None):
        """Constructs a Game instance from a given starting position.

        Args:
            board: Starting board position.
            draw_tracker: Draw tracker to start with.
        """
        self.board = board
        self.turn = Player.white
        self.won = Player.none
        self.draw = False
        self.moves = []

        if draw_tracker is None:
            self._draw_tracker = DrawTracker()
            self._draw_tracker.update(self.board, self.turn)
        else:
            self._draw_tracker = draw_tracker

    def play(self, move):
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
        self.moves.append(move)

        if self.board.is_goal(self.turn):
            self.won = self.turn

        self.turn = Player(not self.turn.value)
        self.draw = self._draw_tracker.update(self.board, self.turn)

        if self.won != Player.none or self.draw:
            self.turn = Player.none

    def copy(self):
        """Returns a deep copy of the game.

        Returns:
            A copy of the current game state.
        """
        game = Game(self.board.copy(), self._draw_tracker.copy())
        game.turn = self.turn
        game.won = self.won
        game.draw = self.draw
        return game
