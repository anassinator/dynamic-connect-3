# -*- coding: utf-8 -*-

from base_board import Board, Player
from winning_boards import generate_winning_boards


class SmallBoard(Board):

    """A 5x4 game board."""

    WIDTH = 5
    HEIGHT = 4
    WINNING_BOARDS = None

    def __init__(self, _white_pieces: int=None, _black_pieces: int=None):
        """Constructs a SmallBoard with all pieces in the correct starting
        position.

        Args:
            _white_pieces: White pieces copy.
            _black_pieces: Black pieces copy.
        """
        super().__init__()

        # Add white pieces.
        if _white_pieces is None:
            self.set(0, 0, Player.white)
            self.set(0, 2, Player.white)
            self.set(self.WIDTH - 1, 1, Player.white)
            self.set(self.WIDTH - 1, 3, Player.white)
        else:
            self._white_pieces = _white_pieces

        # Add black pieces.
        if _black_pieces is None:
            self.set(0, 1, Player.black)
            self.set(0, 3, Player.black)
            self.set(self.WIDTH - 1, 0, Player.black)
            self.set(self.WIDTH - 1, 2, Player.black)
        else:
            self._black_pieces = _black_pieces

    def copy(self) -> "SmallBoard":
        """Returns a deep copy of the board."""
        return SmallBoard(self._white_pieces, self._black_pieces)

    def is_goal(self, player: Player) -> bool:
        """Returns whether the current board is the given player's goal or not.

        Args:
            player: Player to check for.
        """
        if SmallBoard.WINNING_BOARDS is None:
            SmallBoard.WINNING_BOARDS = generate_winning_boards(SmallBoard)
        return super().is_goal(player)


class LargeBoard(Board):

    """A 7x6 game board."""

    WIDTH = 7
    HEIGHT = 6
    WINNING_BOARDS = None

    def __init__(self, _white_pieces: int=None, _black_pieces: int=None):
        """Constructs a LargeBoard with all pieces in the correct starting
        position.

        Args:
            _white_pieces: White pieces copy.
            _black_pieces: Black pieces copy.
        """
        super().__init__()

        # Add white pieces.
        if _white_pieces is None:
            self.set(0, 1, Player.white)
            self.set(0, 3, Player.white)
            self.set(self.WIDTH - 1, 2, Player.white)
            self.set(self.WIDTH - 1, 4, Player.white)
        else:
            self._white_pieces = _white_pieces

        # Add black pieces.
        if _black_pieces is None:
            self.set(0, 2, Player.black)
            self.set(0, 4, Player.black)
            self.set(self.WIDTH - 1, 1, Player.black)
            self.set(self.WIDTH - 1, 3, Player.black)
        else:
            self._black_pieces = _black_pieces

    def copy(self) -> "LargeBoard":
        """Returns a deep copy of the board."""
        return LargeBoard(self._white_pieces, self._black_pieces)

    def is_goal(self, player: Player) -> bool:
        """Returns whether the current board is the given player's goal or not.

        Args:
            player: Player to check for.
        """
        if LargeBoard.WINNING_BOARDS is None:
            LargeBoard.WINNING_BOARDS = generate_winning_boards(LargeBoard)
        return super().is_goal(player)

