# -*- coding: utf-8 -*-

from math import inf, isnan
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
        """
        raise NotImplementedError


class WeightedHeuristic(object):

    """A heuristic and corresponding weight pairing.

    Attributes:
        heuristic: Heuristic.
        weight: Correspoding weight.
    """

    def __init__(self, heuristic: Heuristic, weight: float):
        """Constructs a WeightedHeuristic.

        Args:
            heuristic: Heuristic.
            weight: Corresponding weight.
        """
        self.heuristic = heuristic
        self.weight = weight


class GoalHeuristic(Heuristic):

    """A heuristic based on whether a player has won the game or not."""

    @classmethod
    def compute(cls, board: Board, player: Player) -> float:
        """Computes the heuristic's value for a given game state.

        Args:
            board: Current board.
            player: Current player.

        Returns:
            A white win is represented as +inf and a black win is represented
            as -inf. Anything else returns 0.
        """
        if board.is_goal(Player.white):
            return inf
        elif board.is_goal(Player.black):
            return -inf

        return 0


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
            The number of runs of 2 the player is leading the black player by.
        """
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


class DistanceToCenterHeuristic(Heuristic):

    """A heuristic based on the distance from each piece to the center of the
    board.
    """

    @classmethod
    def compute(cls, board: Board, player: Player) -> float:
        """Computes the heuristic's value for a given game state.

        Args:
            board: Current board.
            player: Current player.

        Returns:
            The difference between the sum of the distances of all black pieces
            from the center minus the sum of the distances of all white pieces
            from the center.
        """
        center_x = (board.WIDTH - 1) / 2
        center_y = (board.HEIGHT - 1) / 2

        white_distance = 0
        black_distance = 0
        for x in range(board.WIDTH):
            for y in range(board.HEIGHT):
                piece = board.get(x, y)
                if piece == Player.none:
                    continue

                distance = abs(x - center_x) + abs(y - center_y)
                if piece == Player.white:
                    white_distance += distance
                else:
                    black_distance += distance

        return black_distance - white_distance


class NumberOfMovesHeuristic(Heuristic):

    """Heuristic based on the number of available moves."""

    @classmethod
    def compute(cls, board: Board, player: Player) -> float:
        """Computes the heuristic's value for a given game state.

        Args:
            board: Current board.
            player: Current player.

        Returns:
            The difference between the number of available moves white can take
            and black can take.
        """
        white_moves = len(list(board.available_moves(Player.white)))
        black_moves = len(list(board.available_moves(Player.black)))
        return white_moves - black_moves


class NumberOfBlockedGoalsHeuristic(Heuristic):

    """Heuristic based on the number of blocked goals."""

    RUNS_OF_THREE = None

    @classmethod
    def compute(cls, board: Board, player: Player) -> float:
        """Computes the heuristic's value for a given game state.

        Args:
            board: Current board.
            player: Current player.

        Returns:
            The difference between the number of blocked white wins and black
            blocked wins.
        """
        if cls.RUNS_OF_THREE is None:
            board_class = type(board)
            cls.RUNS_OF_THREE = generate_streaking_boards(board_class, 3)

        white_blocked = 0
        black_blocked = 0
        all_pieces = board._white_pieces | board._black_pieces
        for win in cls.RUNS_OF_THREE:
            if win & all_pieces == win:
                white_almost_win = win ^ board._white_pieces
                if (white_almost_win & (white_almost_win - 1)) > 0:
                    # More than one bit is set so a white win is blocked.
                    white_blocked += 1
                else:
                    black_blocked += 1

        return white_blocked - black_blocked


class DistanceToGoalHeuristic(Heuristic):

    """Heuristic based on the number of moves to reach goal."""

    RUNS_OF_TWO = None
    RUNS_OF_THREE = None

    @classmethod
    def _distance_to_win(cls, pieces: int, opposite_pieces: int,
                         run_of_three: int, board: Board):
        """Computes the smallest number of moves to reach a winning goal.

        Args:
            pieces: Pieces to consider as an int.
            opposite_pieces: Opposing player's pieces as an int.
            run_of_three: Current run of three to consider.
            board: Board to consider.

        Returns:
            Minimum number of moves to reach goal.
        """
        pieces_coinciding = pieces & run_of_three
        if (pieces_coinciding & (pieces_coinciding - 1)) == 0:
            # Only 0 or 1 pieces are coinciding so don't consider.
            return inf

        destination = run_of_three - pieces_coinciding
        if destination == 0:
            # Goal already achieved.
            return 0

        if (opposite_pieces | pieces) & run_of_three == run_of_three:
            # Blocked by opposite pieces.
            return inf

        movable_pieces_locations = set()
        destination_location = None
        for i in range(board.WIDTH * board.HEIGHT):
            if (pieces_coinciding >> i) & 1:
                x = i % board.WIDTH
                y = i % board.HEIGHT
                movable_pieces_locations.add((x, y))
            if destination_location is None:
                if (destination >> i) & 1:
                    x = i % board.WIDTH
                    y = i % board.HEIGHT
                    destination_location = (x, y)

        closest = inf
        for x, y in movable_pieces_locations:
            dx = abs(x - destination_location[0])
            dy = abs(y - destination_location[1])
            closest = min(closest, dx + dy)

        return closest

    @classmethod
    def compute(cls, board: Board, player: Player) -> float:
        """Computes the heuristic's value for a given game state.

        Args:
            board: Current board.
            player: Current player.

        Returns:
            The difference between the black's distance to winning and the
            white's ditance to winning.
        """
        if cls.RUNS_OF_THREE is None:
            board_class = type(board)
            cls.RUNS_OF_THREE = generate_streaking_boards(board_class, 3)

        white_distance = inf
        black_distance = inf
        for b in cls.RUNS_OF_THREE:
            d = cls._distance_to_win(board._white_pieces, board._black_pieces,
                                     b, board)
            white_distance = min(d, white_distance)

            d = cls._distance_to_win(board._black_pieces, board._white_pieces,
                                     b, board)
            black_distance = min(d, black_distance)

        # print("dist to goal: w {}, b {}".format(white_distance, black_distance))

        value = black_distance - white_distance
        if isnan(value):
            return 0

        return black_distance - white_distance


class TurnHeuristic(Heuristic):

    """Heuristic based on who's turn it is."""

    @classmethod
    def compute(cls, board: Board, player: Player) -> float:
        """Computes the heuristic's value for a given game state.

        Args:
            board: Current board.
            player: Current player.

        Returns:
            1 if it's the white player's turn.
            -1 if it's the black player's turn.
        """
        if player == Player.white:
            return 1
        elif player == Player.black:
            return -1
        else:
            raise NotImplementedError
