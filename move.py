# -*- coding: utf-8 -*-

from enum import Enum


class InvalidMove(Exception):

    """Invalid move exception.
    
    Attributes:
        message: Exception message.
    """

    def __init__(self, message: str):
        """Constructs an InvalidMove with a message.
        
        Args:
            message: Exception message.
        """
        self.message = message


class Direction(Enum):
    
    """Valid move directions."""

    north = 'N'
    east = 'E'
    west = 'W'
    south = 'S'


class Move(object):

    """A game move.
    
    Attributes:
        x: Horizontal index of cell to move.
        y: Vertical index of cell to move.
        direction: Direction to move in.
    """

    def __init__(self, x: int, y: int, direction: Direction):
        """Constructs a Move.
        
        Args:
            x: Horizontal index of cell to move.
            y: Vertical index of cell to move.
            direction: Direction to move in.
        """
        self.x = x
        self.y = y
        self.direction = direction

    @classmethod
    def from_str(cls, s: str) -> "Move":
        """Constructs a Move from a serialized string.
        
        Args:
            s: Serialized string such that the first character is x, the second
               is y and the third is the direction.

        Returns:
            Move.
        """
        if len(s) == 3:
            x, y, d = tuple(s)
            if str.isdigit(x) and str.isdigit(y) and str.isupper(d):
                try:
                    return Move(int(x) - 1, int(y) - 1, Direction(d))
                except ValueError:
                    pass

        raise InvalidMove("Invalid string")

    def __str__(self):
        """Returns a valid string representation of the move.
        
        Returns:
            Serialized move.
        """
        return "{0}{1}{2}".format(self.x + 1, self.y + 1, self.direction.value)

