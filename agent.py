# -*- coding: utf-8 -*-

from game import Game
from move import Move
from typing import List
from base_board import Board, Player
from heuristics import WeightedHeuristic


class Agent(object):

    """An AI agent that plays a given game.
    
    Attributes:
        game: Current game state.
        player: Acting player.
        heuristics: List of weighted heuristics.
    """

    def __init__(self, game: Game, player: Player,
                 heuristics: List[WeightedHeuristic]):
        """Constructs an Agent.

        Args:
            game: Game to play.
            player: Player to play as.
            heuristics: List of weighted heuristics to use.
        """
        self.game = game.copy()
        self.player = player
        self.heuristics = heuristics

    def request_move(self) -> Move:
        """Request the best available move so far.
        
        Returns:
            Best available move agent so far.
        """
        raise NotImplementedError

    def state_updated(self, move: Move, turn: Player) -> None:
        """Notifies the agent that a player has made a move and that the agent
        should observe the new game state.

        Args:
            move: Move played by the player.
            player: Who's turn it is now.
        """
        raise NotImplementedError

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
        for wh in heuristics:
            heuristic += wh.weight * wh.heuristic.compute(board, player)
        return heuristic 

