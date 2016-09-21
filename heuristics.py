# -*- coding: utf-8 -*-

from base_board import Board, Player
from abc import ABCMeta, abstractmethod
from streaking_boards import generate_streaking_boards


class Heuristic(object, metaclass=ABCMeta):

    """A heuristic."""

    @classmethod
    @abstractmethod
    def compute(cls, board: Board, player: Player) -> float:
        """Computes the heuristic's value for a given game state.

        Args:
            board: Current board.
            player: Current player.

        Returns:
            The estimated value of the board such that the more positive it is
            the more in favor of the white player the board is and the more
            negative it is, the more in favor of the black player the board is.

            A white win is represented as +inf and a black win is represented
            as -inf.
        """
        if board.is_goal(Player.white):
            return float("inf")
        elif board.is_goal(Player.black):
            return float("-inf")
        else:
            raise NotImplementedError


class NumberOfRunsOfTwoHeuristic(Heuristic):

    """A heuristic based on the number of runs of 2 pieces.

    H(n) = <# of runs of 2 white pieces> - <# of runs of 2 black pieces>
    """

    RUNS_OF_TWO = None

    @classmethod
    def compute(cls, board: Board, player: Player) -> float:
        """Computes the heuristic's value for a given game state.

        Args:
            board: Current board.
            player: Current player.

        Returns:
            The estimated value of the board such that the more positive it is
            the more in favor of the white player the board is and the more
            negative it is, the more in favor of the black player the board is.

            A white win is represented as +inf and a black win is represented
            as -inf.
        """
        try:
            return super().compute(board, player)
        except NotImplementedError:
            pass

        if cls.RUNS_OF_TWO is None:
            board_class = type(board)
            cls.RUNS_OF_TWO = generate_streaking_boards(board_class, 2)

        white_runs = 0
        black_runs = 0
        for b in cls.RUNS_OF_TWO:
            if b & board._white_pieces == b:
                white_runs += 1
            if b & board._black_pieces == b:
                black_runs += 1

        return white_runs - black_runs

