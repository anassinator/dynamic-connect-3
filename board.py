# -*- coding: utf-8 -*-

import numpy as np
from enum import Enum
from abc import ABCMeta, abstractmethod
from move import Direction, InvalidMove


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
        cells: Array of the game board's cells.

    Cell values are defined such that:
        Player.none.value: Empty cell.
        Player.white.value: Cell occupied by white piece.
        Player.black.value: Cell occupied by black piece.
    """

    def __init__(self, width, height, cells=None):
        """Constructs a Board with the specified width and height.
        
        Args:
            width: Width in number of cells.
            height: Height in number of cells.
            cells: Predetermined cells.
        """
        self.width = width
        self.height = height
        if cells is not None:
            self.cells = cells
        else:
            self.cells = np.zeros((width, height), dtype=np.int8)
            for x in range(width):
                for y in range(height):
                    self.cells[x][y] = Player.none.value

    def __str__(self):
        """Returns a string representation of the game board."""
        s = ""
        Board(3, 2)
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[x][y]
                if cell == Player.none.value:
                    s += ' '
                elif cell == Player.white.value:
                    s += '■'
                elif cell == Player.black.value:
                    s += '□'

                if x != self.width - 1:
                    s += '│'

            if y != self.height - 1:
                s += '\n'

        return s

    @abstractmethod
    def copy(self):
        """Returns a deep copy of the board."""
        raise NotImplementedError

    @abstractmethod
    def is_goal(self, player):
        """Returns whether the current board is the given player's goal or not.

        Args:
            player: Player to check for.
        """
        raise NotImplementedError

    def get(self, x, y):
        """Returns the occupancy of the <x, y> cell.
        
        Args:
            x: Horizontal index on the board.
            y: Vertical index on the board.
        
        Returns:
            Player.none.value if the cell is empty,
            Player.white.value if it's occupied by a white piece, and
            Player.black.value if it's occupied by a black piece.
        """
        return self.cells[x][y]
        
    def set(self, x, y, value):
        """Sets the occupancy of the <x, y> cell.

        Args:
            x: Horizontal index on the board.
            y: Vertical index on the board.
            value: Occupancy of the cell.
        """
        self.cells[x][y] = value

    def move(self, move):
        """Moves a piece on the board in place.
        
        Args:
            move: Move to make.
        """
        current_cell = self.get(move.x, move.y)

        # Check if valid.
        if current_cell == Player.none.value:
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
        self.set(move.x, move.y, Player.none.value)
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

    def __init__(self, cells=None):
        """Constructs a SmallBoard with all pieces in the correct starting
        position.."""
        super().__init__(5, 4, cells)

        if cells is None:
            # Add white pieces.
            self.set(0, 0, Player.white.value)
            self.set(0, 2, Player.white.value)
            self.set(4, 1, Player.white.value)
            self.set(4, 3, Player.white.value)

            # Add black pieces.
            self.set(0, 1, Player.black.value)
            self.set(0, 3, Player.black.value)
            self.set(4, 0, Player.black.value)
            self.set(4, 2, Player.black.value)

    def copy(self):
        """Returns a deep copy of the board."""
        return SmallBoard(self.cells.copy())

    def is_goal(self, player):
        """Returns whether the current board is the given player's goal or not.

        Args:
            player: Player to check for.
        """
        raise NotImplementedError


class LargeBoard(Board):

    """A 7x6 game board."""

    def __init__(self, cells=None):
        """Constructs a LargeBoard with all pieces in the correct starting
        position.."""
        super().__init__(7, 6, cells)

        if cells is None:
            # Add white pieces.
            self.set(0, 1, Player.white.value)
            self.set(0, 3, Player.white.value)
            self.set(6, 2, Player.white.value)
            self.set(6, 4, Player.white.value)

            # Add black pieces.
            self.set(0, 2, Player.black.value)
            self.set(0, 4, Player.black.value)
            self.set(6, 1, Player.black.value)
            self.set(6, 3, Player.black.value)

    def copy(self):
        """Returns a deep copy of the board."""
        return LargeBoard(self.cells.copy())

    def is_goal(self, player):
        """Returns whether the current board is the given player's goal or not.

        Args:
            player: Player to check for.
        """
        raise NotImplementedError
