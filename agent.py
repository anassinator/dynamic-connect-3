# -*- coding: utf-8 -*-

import asyncio
from game import Game
from move import Move
from typing import List
from timeout import timeout
from search import MinimaxSearch
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
        self.searcher = MinimaxSearch(player, heuristics)

    def request_move(self, max_time: int) -> Move:
        """Request the best available move within the time limit provided.

        Args:
            max_time: Max time to think in seconds.

        Returns:
            Best available move agent so far.
        """
        try:
            with timeout(max_time):
                self.searcher.search(self.game.board.copy(), self.game.turn)
        except TimeoutError:
            pass

        return self.searcher.request_move()

    def update_state(self, move: Move, turn: Player) -> None:
        """Notifies the agent that a player has made a move and that the agent
        should observe the new game state.

        Args:
            move: Move played by the player.
            player: Who's turn it is now.
        """
        self.game.play(move)
