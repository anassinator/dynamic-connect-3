# -*- coding: utf-8 -*-

from game import Game
from move import Move
from typing import List
from timeout import timeout
from search import MinimaxSearch
from base_board import Board, Player
from abc import ABCMeta, abstractmethod
from heuristics import WeightedHeuristic


class Agent(object, metaclass=ABCMeta):

    """An agent who can play the game.
    
    Attributes:
        player: Acting player.
    """

    def __init__(self, player: Player):
        """Constructs the Agent.

        Args:
            player: Player to play as.
        """
        if player == Player.none:
            raise NotImplementedError

        self.player = player
        self._game = None

    def play(self, game: Game):
        """Starts playing a game.
        
        Args:
            game: A copy of the game to play on.
        """
        self._game = game

    def update(self, move: Move):
        """Updates game with a given move.
        
        Args:
            move: Move.
        """
        self._game.play(move)

    @abstractmethod
    def yield_move(self, max_time: float) -> Move:
        """Yields a move to play.
        
        Args:
            max_time: Max time to come up with a move in seconds.

        Raises:
            PlayerResigned: If the agent resigns.
        """
        raise NotImplementedError


class HumanAgent(Agent):

    """A human agent that plays the game.
    
    Attributes:
        player: Acting player.
    """
    
    def yield_move(self, max_time: float) -> Move:
        """Yields a move to play.
        
        Args:
            max_time: Max time to come up with a move in seconds.

        Returns:
            Move.

        Raises:
            PlayerResigned: If the agent resigns.
        """
        try:
            s = input("Enter a move: ")
            return Move.from_str(s)
        except (KeyboardInterrupt, EOFError):
            raise PlayerResigned

        return move


class AutonomousAgent(Agent):

    """An AI agent that plays a given game.
    
    Attributes:
        player: Acting player.
    """

    def __init__(self, player: Player, heuristics: List[WeightedHeuristic]):
        """Constructs an AutonomousAgent.

        Args:
            player: Player to play as.
            heuristics: List of weighted heuristics to use.
        """
        super().__init__(player)
        self._heuristics = heuristics
        self._searcher = MinimaxSearch(player, heuristics)

    def yield_move(self, max_time: float) -> Move:
        """Yields a move to play.
        
        Args:
            max_time: Max time to come up with a move in seconds.

        Returns:
            Best available move so far.

        Raises:
            PlayerResigned: If the agent resigns.
        """
        print("Thinking... ", end="")
        try:
            with timeout(max_time):
                self._searcher.search(self._game.board.copy(), self._game.turn)
        except TimeoutError:
            pass

        move = self._searcher.request_move()
        print(move)

        return move
