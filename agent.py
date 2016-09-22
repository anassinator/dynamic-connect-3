# -*- coding: utf-8 -*-

from game import Game
from move import Move
from typing import List
from threading import Lock
from base_board import Board, Player
from heuristics import WeightedHeuristic


class Agent(object):

    """An AI agent that plays a given game.
    
    Attributes:
        game: Current game state.
        player: Acting player.
        heuristics: List of weighted heuristics.
    """

    def __init__(self, board: Board, player: Player,
                 heuristics: List[WeightedHeuristic]):
        """Constructs an Agent.

        Args:
            board: Board to play on.
            player: Player to play as.
            heuristics: List of weighted heuristics to use.
        """
        self.game = Game(board.copy())
        self.player = player
        self.heuristics = heuristics
        self.__lock = Lock()

    def request_move(self) -> Move:
        """Request the best available move so far.

        Returns:
            Best available move agent so far.
        """
        with self.__lock:
            board = self.game.board
            turn = self.game.turn

        move, value = self._minimax(board, turn, 5)

        return move

    def update_state(self, move: Move, turn: Player) -> None:
        """Notifies the agent that a player has made a move and that the agent
        should observe the new game state.

        Args:
            move: Move played by the player.
            player: Who's turn it is now.
        """
        with self.__lock:
            self.game.play(move)

    def __compute_heuristic(self, board: Board, player: Player) -> float:
        """Computes the weighted heuristic for the game state given.

        Args:
            board: Board to analyze.
            player: Player's turn.

        Returns:
            The estimated value of the board such that the more positive it is
            the more in favor of the white player the board is and the more
            negative it is, the more in favor of the black player the board is.
            This is effectively a weighted sum of all the heuristics this agent
            considers.
        """
        heuristic = 0
        for wh in self.heuristics:
            heuristic += wh.weight * wh.heuristic.compute(board, player)
        return heuristic 

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
        if turn == Player.white:
            return current_value > best_value
        elif turn == Player.black:
            return current_value < best_value
        else:
            raise NotImplementedError

    def _minimax(self, board: Board, turn: Player, max_depth: int):
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
            return (None, self.__compute_heuristic(board, turn))

        best_move = None
        best_value = None
        for move in board.available_moves(turn):
            child_board = board.copy()
            child_board.move(move)
            _, v = self._minimax(child_board, next_turn, max_depth - 1)
            if self.__minimax_comparator(best_value, v, turn):
                best_value = v
                best_move = move

        return (best_move, best_value)

