# -*- coding: utf-8 -*-

from collections import Counter


class DrawTracker(object):

    """Tracks whether a draw has occured yet or not."""

    def __init__(self, counter=None):
        """Constructs a DrawTracker.

        Args:
            state: Current counter.
        """
        if counter is None:
            self.counter = Counter()
        else:
            self.counter = counter.copy()

    def update(self, board, turn):
        """Adds a new board to the count and determines if it's a draw by the
        threefold repetition rule.

        Args:
            board: New board state.
            turn: Current player's turn.

        Returns:
            Whether this move makes for a draw.
        """
        state = (board._white_pieces, board._black_pieces, turn.value)
        self.counter.update([state])
        if self.counter[state] >= 3:
            return True
        return False

    def copy(self):
        """Returns a deep copy of the current tracker.

        Returns:
            A copy of the draw tracker.
        """
        return DrawTracker(self.counter)
