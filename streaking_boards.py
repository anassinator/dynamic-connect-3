# -*- coding: utf-8 -*-

from base_board import Board, Player


def _consecutive(l, n):
    """Yields all consecutive n elements from an enumerator.
    
    Args:
        l: Enumerator.
        n: Number of elements to take at a time.
    
    Yields:
        All consecutive n numbers as tuples.
    """
    for t in zip(*(l[x:] for x in range(n))):
        yield t


def generate_streaking_boards(board_class, n):
    """Generates all streaks for a given board type as ints.
    
    Argsstreaking:
        board_class: Board class type.
        n: Length of streaks.

    Returns:
        Set of all streaking states.
    """
    states = set()
    width, height = board_class.WIDTH, board_class.HEIGHT
    
    # Generate all horizontal streaking boards.
    for y in range(height):
        for t in _consecutive(range(width), n):
            board = board_class(0, 0)
            for x in t:
                 board.set(x, y, Player.white)
            states.add(board._white_pieces) 

    # Generate all vertical streaking boards.
    for x in range(width):
        for t in _consecutive(range(height), n):
            board = board_class(0, 0)
            for y in t:
                board.set(x, y, Player.white)
            states.add(board._white_pieces) 

    # Generate all left-to-right diagonal streaking boards.
    for x in range(width - n + 1):
        for t in _consecutive(range(height), n):
            board = board_class(0, 0)
            for i, y in enumerate(t):
                 board.set(x + i, y, Player.white)
            states.add(board._white_pieces) 

    # Generate all right-to-left diagonal streaking boards.
    for x in range(width - n + 1):
        for t in _consecutive(range(height), n):
            board = board_class(0, 0)
            for i, y in enumerate(t):
                 board.set(x + n - 1 - i, y, Player.white)
            states.add(board._white_pieces) 

    return states


def generate_winning_boards(board_class):
    """Generates all winning states for a given board type as ints.
    
    Args:
        board_class: Board class type.

    Returns:
        Set of all winning states.
    """
    return generate_streaking_boards(board_class, 3)
