# -*- coding: utf-8 -*-

from typing import Generator, Type
from base_board import Board, Player


def _consecutive_triplets(l: Generator[int, None, None]):
    """Yields all consecutive triplets from an enumerator.
    
    Args:
        l: Enumerator.
    
    Yields:
        All consecutive triplets as tuples.
    """
    for first, second, third in zip(l, l[1:], l[2:]):
        yield (first, second, third)


def generate_winning_boards(board_class: Type[Board]):
    """Generates all winning states for a given board type as ints.
    
    Args:
        board_class: Board class type.

    Returns:
        Set of winning states.
    """
    states = set()
    width, height = board_class.WIDTH, board_class.HEIGHT
    
    # Generate all horizontal winning boards.
    for y in range(height):
        for first, second, third in _consecutive_triplets(range(width)):
            board = board_class(0, 0)
            board.set(first, y, Player.white)
            board.set(second, y, Player.white)
            board.set(third, y, Player.white)
            states.add(board._white_pieces) 

    # Generate all vertical winning boards.
    for x in range(width):
        for first, second, third in _consecutive_triplets(range(height)):
            board = board_class(0, 0)
            board.set(x, first, Player.white)
            board.set(x, second, Player.white)
            board.set(x, third, Player.white)
            states.add(board._white_pieces) 

    # Generate all left-to-right diagonal winning boards.
    for x in range(width - 2):
        for first, second, third in _consecutive_triplets(range(height)):
            board = board_class(0, 0)
            board.set(x, first, Player.white)
            board.set(x + 1, second, Player.white)
            board.set(x + 2, third, Player.white)
            states.add(board._white_pieces) 

    # Generate all right-to-left diagonal winning boards.
    for x in range(width - 2):
        for first, second, third in _consecutive_triplets(range(height)):
            board = board_class(0, 0)
            board.set(x, third, Player.white)
            board.set(x + 1, second, Player.white)
            board.set(x + 2, first, Player.white)
            states.add(board._white_pieces) 

    return states

