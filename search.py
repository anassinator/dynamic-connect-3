# -*- coding: utf-8 -*-

import itertools
from base_board import Player
from abc import ABCMeta, abstractmethod

try:
    from math import inf
except ImportError:
    inf = float("inf")


class NoSolutionFound(Exception):

    """No solution was found."""

    pass


class Search(object, metaclass=ABCMeta):

    """Asynchronous search.

    Attributes:
        player: Player searching for.
        heuristics: List of weighted heuristics to use.
    """

    def __init__(self, player, heuristics):
        """Constructs a Search using the provided heuristics.

        Args:
            player: Player to search for.
            heuristics: List of weighted heuristics to use.
        """
        self.player = player
        self.heuristics = heuristics

    @abstractmethod
    def search(self, state):
        """Starts an indefinite search from the given root board with the given
        player's turn.

        The longer this search runs, the better the solution provided. One
        should cancel this task once it has been long enough, and then
        request a move.

        Args:
            state: Current game state.
        """
        raise NotImplementedError

    @abstractmethod
    def request_move(self):
        """Requests the current best solution.

        Returns:
            Move.

        Raises:
            NoSolutionFound: If no solution has been found yet.
        """
        raise NotImplementedError


class MinimaxSearch(Search):

    """Asynchronous minimax search."""

    def __init__(self, player, heuristics, transposition_table):
        """Constructs a Search using the provided heuristics.

        Args:
            player: Player to search for.
            heuristics: List of weighted heuristics to use.
            transposition_table: Transposition table.
        """
        super().__init__(player, heuristics)
        self._best_move_yet = None
        self._depth = 0
        self._transposition_table = transposition_table

    def search(self, state):
        """Starts an indefinite search from the given root board with the given
        player's turn.

        The longer this search runs, the better the solution provided. One
        should cancel this task once it has been long enough, and then
        request a move.

        Args:
            state: Current game state.
        """
        self._best_next_move = None
        self._moves = 0
        self._positions = 0

        for depth in itertools.count():
            root = state.copy()
            self._best_next_move, value = self._search(root, 0, depth)
            self._depth = depth
            if (root, depth) not in self._transposition_table:
                self._transposition_table[(root, depth)] = value

    def request_move(self):
        """Requests the current best solution.

        Returns:
            Move.

        Raises:
            NoSolutionFound: If no solution has been found yet.
        """
        if self._best_next_move:
            print("Searched up to {} moves deep: ".format(self._depth), end="")
            return self._best_next_move
        else:
            raise NoSolutionFound

    def _heuristics_key(self, child):
        """Computes the weighted heuristics of a child game state.

        Args:
            child: Tuple of (move, game state).

        Returns:
            Computed heuristic.
        """
        _, state = child
        return state.compute_heuristic(self.heuristics)

    def _search(self, state, curr_depth, max_depth):
        """Searches for the best move given the current board state by looking
        up to a certain depth.

        Args:
            state: Game state.
            curr_depth: Current depth looking at.
            max_depth: Max depth to look at.

        Returns:
            Tuple of the (best move, its value).
        """
        if state.won_by() != Player.none:
            # Favor closer wins.
            v = state.compute_heuristic(self.heuristics)
            return (None, v / curr_depth)
        if curr_depth == max_depth:
            return (None, state.compute_heuristic(self.heuristics))

        best_move = None
        best_value = None

        if state.turn == Player.white:
            children = sorted(state.next_states(), key=self._heuristics_key,
                              reverse=True)
        else:
            children = sorted(state.next_states(), key=self._heuristics_key)

        depth_to_search = max_depth - curr_depth
        for move, child in children:
            # Check if this board had been analyzed to this depth before.
            if (child, depth_to_search) in self._transposition_table:
                v = self._transposition_table[(child, depth_to_search)]
            else:
                _, v = self._search(child, curr_depth + 1, max_depth)
                self._transposition_table[(child, depth_to_search)] = v

            if self._minimax_comparator(best_value, v, state.turn):
                best_move = move
                best_value = v

        return (best_move, best_value)

    def _minimax_comparator(self, best_value, current_value, turn):
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

    def _search(self, state, curr_depth, max_depth, alpha=-inf, beta=inf):
        """Searches for the best move given the current board state by looking
        up to a certain depth.

        Args:
            state: Game state.
            curr_depth: Current depth looking at.
            max_depth: Max depth to look at.
            alpha: Alpha.
            beta: Beta.

        Returns:
            Tuple of the (best move, its value).
        """
        if state.won_by() != Player.none:
            # Favor closer wins.
            v = state.compute_heuristic(self.heuristics)
            return (None, v / curr_depth)
        if curr_depth == max_depth:
            return (None, state.compute_heuristic(self.heuristics))

        best_move = None
        best_value = None

        if state.turn == Player.white:
            children = sorted(state.next_states(), key=self._heuristics_key,
                              reverse=True)
        else:
            children = sorted(state.next_states(), key=self._heuristics_key)

        depth_to_search = max_depth - curr_depth
        for move, child in children:
            # Check if this board had been analyzed to this depth before.
            if (child, depth_to_search) in self._transposition_table:
                v = self._transposition_table[(child, depth_to_search)]
            else:
                _, v = self._search(child, curr_depth + 1, max_depth,
                                    alpha, beta)
                self._transposition_table[(child, depth_to_search)] = v

            if self._minimax_comparator(best_value, v, state.turn):
                best_move = move
                best_value = v

            if curr_depth == 0:
                print("depth: {}, considering: {}, move: {}, best: {}"
                      .format(max_depth, str(move), v, str(best_move)))

            if best_value is not None and state.turn == Player.white:
                alpha = max(alpha, best_value)
            elif best_value is not None and state.turn == Player.black:
                beta = min(beta, best_value)

            if alpha >= beta:
                break

        return (best_move, best_value)
