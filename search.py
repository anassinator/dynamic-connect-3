# -*- coding: utf-8 -*-

import asyncio
import itertools
from move import Move
from typing import List
from threading import Lock
from base_board import Board, Player
from abc import ABCMeta, abstractmethod
from heuristics import WeightedHeuristic


class NoSolutionFound(Exception):

    """No solution was found."""

    pass


class GameState(object):

    """Game state."""

    def __init__(self, board: Board, turn: Player):
        """Constructs a GameState.

        Args:
            board: Board.
            turn: Player's turn.
        """
        self.board = board
        self.turn = turn


class TranspositionTable(object):

    """Transposition table."""

    def __init__(self):
        """Constructs a TranspositionTable."""
        self._table = set()

    def _hash(self, state: GameState):
        """Hashes a game state into a unique number.
 
        Args:
            state: Game state.

        Returns:
            Unique number.
        """
        board, turn = state.board, state.turn
        length = board.WIDTH * board.HEIGHT
        hashed = board._white_pieces
        hashed += board._black_pieces << length
        hashed += turn.value << length + 1
        return hashed

    def add(self, state: GameState):
        """Adds a game state to the transposition table.

        Args:
            state: Game state.
        """
        hashed = self._hash(state)
        self._table.add(hashed)

    def __contains__(self, state: GameState):
        """Returns whether the transposition table contains a game state.

        Args:
            state: Game state.

        Returns:
            Whether the game state is in the transposition table or not.
        """
        hashed = self._hash(state)
        return self._table.__contains__(hashed)

    def __len__(self):
        """Returns the number of elements in the transposition table."""
        return len(self._table)


class Search(object, metaclass=ABCMeta):

    """Asynchronous search.

    Attributes:
        player: Player searching for.
        heuristics: List of weighted heuristics to use.
    """

    def __init__(self, player: Player, heuristics: List[WeightedHeuristic]):
        """Constructs a Search using the provided heuristics.

        Args:
            player: Player to search for.
            heuristics: List of weighted heuristics to use.
        """
        self.player = player
        self.heuristics = heuristics

    def _compute_heuristic(self, board: Board, turn: Player) -> float:
        """Computes the weighted heuristic for the game state given.

        Args:
            board: Board to analyze.
            turn: Player's turn.

        Returns:
            The estimated value of the board such that the more positive it is
            the more in favor of the white player the board is and the more
            negative it is, the more in favor of the black player the board is.
            This is effectively a weighted sum of all the heuristics this agent
            considers.
        """
        heuristic = 0
        for wh in self.heuristics:
            heuristic += wh.weight * wh.heuristic.compute(board, turn)
        return heuristic

    @abstractmethod
    def search(self, board: Board, turn: Player):
        """Starts an indefinite search from the given root board with the given
        player's turn.

        The longer this search runs, the better the solution provided. One
        should cancel this task once it has been long enough, and then
        request a move.

        Args:
            board: Current board configuration.
            turn: Current turn.
            loop: Event loop.
        """
        raise NotImplementedError

    @abstractmethod
    def request_move(self) -> Move:
        """Requests the current best solution.

        Returns:
            Move.

        Raises:
            NoSolutionFound: If no solution has been found yet.
        """
        raise NotImplementedError


class MinimaxSearch(Search):

    """Asynchronous minimax search."""

    def __init__(self, player: Player, heuristics: List[WeightedHeuristic]):
        """Constructs a Search using the provided heuristics.

        Args:
            player: Player to search for.
            heuristics: List of weighted heuristics to use.
        """
        super().__init__(player, heuristics)
        self._best_move_yet = None
        self._transposition_table = None
        self._depth = 0
        self._positions = 0

    def search(self, board: Board, turn: Player, start_depth: int=1):
        """Starts an indefinite search from the given root board with the given
        player's turn.

        The longer this search runs, the better the solution provided. One
        should cancel this task once it has been long enough, and then
        request a move.

        Args:
            board: Current board configuration.
            turn: Current turn.
            start_depth: Depth to start searching at.
        """
        self._best_next_move = None
        self._moves = 0
        for depth in itertools.count(start_depth):
            self._transposition_table = TranspositionTable()
            self._best_next_move = self._minimax(board.copy(), turn, depth)
            self._positions += len(self._transposition_table)
            self._depth = depth

    def request_move(self) -> Move:
        """Requests the current best solution.

        Returns:
            Move.

        Raises:
            NoSolutionFound: If no solution has been found yet.
        """
        if self._best_next_move:
            s = ("Considered {} positions {} moves ahead: "
                 .format(self._positions, self._depth))
            print(s, end="")
            return self._best_next_move
        else:
            raise NoSolutionFound

    def _minimax(self, board: Board, turn: Player, max_depth: int):
        """Selects the best move given the current board state by looking up to
        a certain depth.

        Args:
            board: Current root board state.
            turn: Current player's turn.
            max_depth: Max depth to look at.

        Returns:
            Best next move.
        """
        move, _ = self.__minimax(board, turn, max_depth)
        return move

    def __minimax_comparator(self, best_value: float, current_value: float,
                             turn: Player) -> bool:
        """Compares heuristic values based on the turn such that each player
        plays their optimal move.

        The black player tries to minimize the heuristic value, whereas the
        white player tries to maximize it.

        Args:
            best_value: Current best value.
            current_value: Current heuristic value to evaluate.
            turn: Current player's turn.

        Return:
            Whether the current value is better or not.
        """
        if best_value is None:
            return True
        elif current_value is None:
            return False

        if turn == Player.white:
            return current_value > best_value
        elif turn == Player.black:
            return current_value < best_value
        else:
            raise NotImplementedError

    def __minimax(self, board: Board, turn: Player, max_depth: int):
        """Selects the best move given the current board state by looking up to
        a certain depth.

        Args:
            board: Current root board state.
            turn: Current player's turn.
            max_depth: Max depth to look at.

        Returns:
            Tuple of (best move, heuristic value).
        """
        next_turn = Player.black if turn == Player.white else Player.white
        if max_depth == 0 or board.is_goal(next_turn):
            return (None, self._compute_heuristic(board, turn))

        best_move = None
        best_value = None
        for move in board.available_moves(turn):
            child_board = board.copy()
            child_board.move(move)

            game_state = GameState(child_board, next_turn)
            if game_state in self._transposition_table:
                continue
            else:
                self._transposition_table.add(game_state)

            _, v = self.__minimax(child_board, next_turn, max_depth - 1)
            if self.__minimax_comparator(best_value, v, turn):
                best_value = v
                best_move = move

        return (best_move, best_value)
