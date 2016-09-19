# -*- coding: utf-8 -*-

from enum import Enum
from abc import ABCMeta, abstractmethod
from move import Direction, Move, InvalidMove


class Player(Enum):

    """Player."""

    none = -1
    white = 0
    black = 1


class Board(object, metaclass=ABCMeta):

    """Game board.
    
    Attributes:
        width: Width of the board in number of cells.
        height: Height of the board in number of cells.

    Cell values are defined such that:
        Player.none.value: Empty cell.
        Player.white.value: Cell occupied by white piece.
        Player.black.value: Cell occupied by black piece.
    """

    def __init__(self, width: int, height: int):
        """Constructs a Board with the specified width and height.
        
        Args:
            width: Width in number of cells.
            height: Height in number of cells.
            cells: Array of the game board's cells.
        """
        self.width = width
        self.height = height
        self._white_pieces = 0
        self._black_pieces = 0

    def __str__(self):
        """Returns a string representation of the game board."""
        s = ""
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get(x, y)
                if cell == Player.none:
                    s += ' '
                elif cell == Player.white:
                    s += '■'
                elif cell == Player.black:
                    s += '□'

                if x != self.width - 1:
                    s += '│'

            if y != self.height - 1:
                s += '\n'

        return s

    @abstractmethod
    def copy(self) -> "Board":
        """Returns a deep copy of the board."""
        raise NotImplementedError

    @abstractmethod
    def is_goal(self, player: Player) -> bool:
        """Returns whether the current board is the given player's goal or not.

        Args:
            player: Player to check for.
        """
        raise NotImplementedError

    def get(self, x: int, y: int) -> int:
        """Returns the occupancy of the <x, y> cell.
        
        Args:
            x: Horizontal index on the board.
            y: Vertical index on the board.
        
        Returns:
            Player.none if the cell is empty,
            Player.white if it's occupied by a white piece, and
            Player.black if it's occupied by a black piece.
        """
        index = x + y * self.width
        if (self._white_pieces >> index) & 1:
            return Player.white
        elif (self._black_pieces >> index) & 1:
            return Player.black
        else:
            return Player.none
        
    def set(self, x: int, y: int, player: Player):
        """Sets the occupancy of the <x, y> cell.

        Args:
            x: Horizontal index on the board.
            y: Vertical index on the board.
            player: Player.
        """
        index = x + y * self.width
        if player == Player.white:
            self._white_pieces |= 1 << index
            self._black_pieces &= ~(1 << index)
        elif player == Player.black:
            self._white_pieces &= ~(1 << index)
            self._black_pieces |= 1 << index
        else:
            self._white_pieces &= ~(1 << index)
            self._black_pieces &= ~(1 << index)

    def move(self, move: Move):
        """Moves a piece on the board in place.
        
        Args:
            move: Move to make.
        """
        current_cell = self.get(move.x, move.y)

        # Check if valid.
        if current_cell == Player.none:
            raise InvalidMove("Cell cannot be empty")
        if move.x == 0 and move.direction == Direction.west:
            raise InvalidMove("Reached left edge of board")
        if move.x == self.width - 1 and move.direction == Direction.east:
            raise InvalidMove("Reached right edge of board")
        if move.y == 0 and move.direction == Direction.north:
            raise InvalidMove("Reached top edge of board")
        if move.y == self.height - 1 and move.direction == Direction.south:
            raise InvalidMove("Reached bottom edge of board")

        # Move.
        self.set(move.x, move.y, Player.none)
        if move.direction == Direction.north:
            self.set(move.x, move.y - 1, current_cell)
        elif move.direction == Direction.south:
            self.set(move.x, move.y + 1, current_cell)
        elif move.direction == Direction.east:
            self.set(move.x + 1, move.y, current_cell)
        elif move.direction == Direction.west:
            self.set(move.x - 1, move.y, current_cell)


class SmallBoard(Board):

    """A 5x4 game board."""

    def __init__(self, _white_pieces: int=None, _black_pieces: int=None):
        """Constructs a SmallBoard with all pieces in the correct starting
        position.

        Args:
            _white_pieces: White pieces copy.
            _black_pieces: Black pieces copy.
        """
        super().__init__(5, 4)

        # Add white pieces.
        if _white_pieces is None:
            self.set(0, 0, Player.white)
            self.set(0, 2, Player.white)
            self.set(4, 1, Player.white)
            self.set(4, 3, Player.white)
        else:
            self._white_pieces = _white_pieces

        # Add black pieces.
        if _black_pieces is None:
            self.set(0, 1, Player.black)
            self.set(0, 3, Player.black)
            self.set(4, 0, Player.black)
            self.set(4, 2, Player.black)
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
        raise NotImplementedError


class LargeBoard(Board):

    """A 7x6 game board."""

    def __init__(self, _white_pieces: int=None, _black_pieces: int=None):
        """Constructs a LargeBoard with all pieces in the correct starting
        position.

        Args:
            _white_pieces: White pieces copy.
            _black_pieces: Black pieces copy.
        """
        super().__init__(7, 6)

        # Add white pieces.
        if _white_pieces is None:
            self.set(0, 1, Player.white)
            self.set(0, 3, Player.white)
            self.set(6, 2, Player.white)
            self.set(6, 4, Player.white)
        else:
            self._white_pieces = _white_pieces

        # Add black pieces.
        if _black_pieces is None:
            self.set(0, 2, Player.black)
            self.set(0, 4, Player.black)
            self.set(6, 1, Player.black)
            self.set(6, 3, Player.black)
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
        raise NotImplementedError

