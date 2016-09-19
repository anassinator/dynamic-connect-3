# -*- coding: utf-8 -*-

from enum import Enum
from move import Direction, Move, InvalidMove
from abc import ABCMeta, abstractmethod, abstractproperty


class Player(Enum):

    """Player."""

    none = -1
    white = 0
    black = 1


class Board(object, metaclass=ABCMeta):

    """Game board.
    
    Attributes:
        self.WIDTH: Width of the board in number of cells.
        self.HEIGHT: Height of the board in number of cells.

    Cell values are defined such that:
        Player.none.value: Empty cell.
        Player.white.value: Cell occupied by white piece.
        Player.black.value: Cell occupied by black piece.
    """

    WIDTH = 0
    HEIGHT = 0
    WINNING_BOARDS = set()

    def __init__(self):
        "Constructs a Board with the specified width and height. """
        self._white_pieces = 0
        self._black_pieces = 0

    def __str__(self):
        """Returns a string representation of the game board."""
        s = ""
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                cell = self.get(x, y)
                if cell == Player.none:
                    s += ' '
                elif cell == Player.white:
                    s += '■'
                elif cell == Player.black:
                    s += '□'

                if x != self.WIDTH - 1:
                    s += '│'

            if y != self.HEIGHT - 1:
                s += '\n'

        return s

    @abstractmethod
    def copy(self) -> "Board":
        """Returns a deep copy of the board."""
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
        index = x + y * self.WIDTH
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
        index = x + y * self.WIDTH
        if player == Player.white:
            self._white_pieces |= 1 << index
            self._black_pieces &= ~(1 << index)
        elif player == Player.black:
            self._white_pieces &= ~(1 << index)
            self._black_pieces |= 1 << index
        else:
            self._white_pieces &= ~(1 << index)
            self._black_pieces &= ~(1 << index)

    def available_moves(self, player: Player):
        """Yields all available moves for a given player.
        
        Args:
            player: Player to get available moves for.

        Yields:
            All available moves for a given player.
        """
        pieces = 0
        if player == Player.white:
            pieces = self._white_pieces
        elif player == Player.black:
            pieces = self._black_pieces
        else:
            raise ValueError("Only white and black players can move")

        max_width, max_height = self.WIDTH - 1, self.HEIGHT - 1
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                index = x + y * self.WIDTH
                if (pieces >> index) & 1:
                    if x != 0 and self.get(x - 1, y) == Player.none:
                        yield Move(x, y, Direction.west)
                    if x != max_width and self.get(x + 1, y) == Player.none:
                        yield Move(x, y, Direction.east)
                    if y != 0 and self.get(x, y - 1) == Player.none:
                        yield Move(x, y, Direction.north)
                    if y != max_height and self.get(x, y + 1) == Player.none:
                        yield Move(x, y, Direction.south)

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
        if move.x == self.WIDTH - 1 and move.direction == Direction.east:
            raise InvalidMove("Reached right edge of board")
        if move.y == 0 and move.direction == Direction.north:
            raise InvalidMove("Reached top edge of board")
        if move.y == self.HEIGHT - 1 and move.direction == Direction.south:
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

    def is_goal(self, player: Player) -> bool:
        """Returns whether the current board is the given player's goal or not.

        Args:
            player: Player to check for.
        """
        pieces = 0
        if player == Player.white:
            pieces = self._white_pieces
        elif player == Player.black:
            pieces = self._black_pieces
        else:
            raise ValueError("Only white or black can win")

        for b in self.WINNING_BOARDS:
            if (b & pieces) == b:
                return True

        return False

