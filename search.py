# -*- coding: utf-8 -*-

import itertools
from math import inf
from move import Move
from typing import List
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
        self._next_turn = (Player.black if turn == Player.white else
                           Player.white)

    def __eq__(self, other: "GameState") -> bool:
        """Returns whether two game states are equal or not.
        
        Args:
            other: Game state to compare to.

        Returns:
            Whether the two game states are equivalent or not.
        """
        return (self.board._white_pieces == other.board._white_pieces and
                self.board._black_pieces == other.board._black_pieces and
                self.turn == other.turn)

    def __hash__(self):
        """Hashes the current game state into a unique integer.

        Returns:
            Hashed value.
        """
        return hash((self.board._white_pieces,
                     self.board._black_pieces,
                     self.turn))

    def won_by(self):
        """Returns who won the current game state."""
        if self.board.is_goal(Player.white):
            return Player.white
        elif self.board.is_goal(Player.black):
            return Player.black
        else:
            return Player.none

    def next_states(self):
        """Yields all possible next states.

        Yields:
            Tuple of (move, resulting game state).
        """
        for move in self.board.available_moves(self.turn):
            child_board = self.board.copy()
            child_board.move(move)
            yield (move, GameState(child_board, self._next_turn))


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

    def _compute_heuristic(self, state: GameState) -> float:
        """Computes the weighted heuristic for the game state given.

        Args:
            state: Game state to analyze.

        Returns:
            The estimated value of the board such that the more positive it is
            the more in favor of the white player the board is and the more
            negative it is, the more in favor of the black player the board is.
            This is effectively a weighted sum of all the heuristics this agent
            considers.
        """
        heuristic = 0
        board, turn = state.board, state.turn
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
        self._depth = 0
        self._positions = 0
        self._transposition_table = dict()

    def search(self, board: Board, turn: Player):
        """Starts an indefinite search from the given root board with the given
        player's turn.

        The longer this search runs, the better the solution provided. One
        should cancel this task once it has been long enough, and then
        request a move.

        Args:
            board: Current board configuration.
            turn: Current turn.
        """
        self._best_next_move = None
        self._moves = 0
        self._positions = 0

        for depth in itertools.count():
            state = GameState(board.copy(), turn)
            old_positions = len(self._transposition_table)
            self._best_next_move, _ = self._search(state, depth, set())
            self._positions += len(self._transposition_table) - old_positions
            self._depth = depth

    def request_move(self) -> Move:
        """Requests the current best solution.

        Returns:
            Move.

        Raises:
            NoSolutionFound: If no solution has been found yet.
        """
        if self._best_next_move:
            s = ("Considered {} new positions ({} total) up to {} moves deep: "
                 .format(self._positions, len(self._transposition_table),
                         self._depth))
            print(s, end="")
            return self._best_next_move
        else:
            raise NoSolutionFound

    def _search(self, state: GameState, max_depth: int, visited: set):
        """Searches for the best move given the current board state by looking
        up to a certain depth.

        Args:
            state: Game state.
            max_depth: Max depth to look at.
            visited: Set of visited game states.

        Returns:
            Tuple of the (best move, its value).
        """
        if max_depth == 0 or state.won_by() != Player.none:
            return (None, self._compute_heuristic(state))

        best_move = None
        best_value = None
        for move, child in state.next_states():
            # Check if this board had been visited within this search to avoid
            # loops.
            if child in visited:
                continue
            else:
                visited.add(child)

            # Check if this board had been analyzed to this depth before.
            if (child, max_depth) in self._transposition_table:
                v = self._transposition_table[(child, max_depth)]
            else:
                _, v = self._search(child, max_depth - 1, visited)
                self._transposition_table[(child, max_depth)] = v

            if self._minimax_comparator(best_value, v, state.turn):
                best_move = move
                best_value = v

        return (best_move, best_value)

    def _minimax_comparator(self, best_value: float, current_value: float,
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


class AlphaBetaPrunedMinimaxSearch(MinimaxSearch):

    """Minimax search with alpha-beta pruning."""

    def _search(self, state: GameState, max_depth: int, visited: set,
                 alpha: float=-inf, beta: float=inf):
        """Searches for the best move given the current board state by looking
        up to a certain depth.

        Args:
            state: Game state.
            max_depth: Max depth to look at.
            alpha: Alpha.
            beta: Beta.
            visited: Set of visited game states.

        Returns:
            Tuple of the (best move, its value).
        """
        if max_depth == 0 or state.won_by() != Player.none:
            return (None, self._compute_heuristic(state))

        best_move = None
        best_value = None
        for move, child in state.next_states():
            # Check if this board had been visited within this search to avoid
            # loops.
            if child in visited:
                continue
            else:
                visited.add(child)

            # Check if this board had been analyzed to this depth before.
            if (child, max_depth) in self._transposition_table:
                v = self._transposition_table[(child, max_depth)]
            else:
                _, v = self._search(child, max_depth - 1, visited, alpha, beta)
                self._transposition_table[(child, max_depth)] = v

            if self._minimax_comparator(best_value, v, state.turn):
                best_move = move
                best_value = v

            if best_value is not None and state.turn == Player.white:
                alpha = max(alpha, best_value)
            elif best_value is not None and state.turn == Player.black:
                beta = min(beta, best_value)

            if alpha > beta:
                break

        return (best_move, best_value)
