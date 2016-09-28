# -*- coding: utf-8 -*-

from learner import Learner
from timeout import timeout
from base_board import Player
from move import Move, PlayerResigned
from abc import ABCMeta, abstractmethod


class Agent(object, metaclass=ABCMeta):

    """An agent who can play the game.

    Attributes:
        player: Acting player.
    """

    def __init__(self, player):
        """Constructs the Agent.

        Args:
            player: Player to play as.
        """
        if player == Player.none:
            raise NotImplementedError

        self.player = player
        self._game = None
        self._root_board = None

    def play(self, game):
        """Starts playing a game.

        Args:
            game: A copy of the game to play on.
        """
        self._game = game
        self._root_board = game.board.copy()

    def update(self, move):
        """Updates game with a given move.

        Args:
            move: Move.
        """
        self._game.play(move)

    @abstractmethod
    def yield_move(self, max_time):
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

    def yield_move(self, max_time):
        """Yields a move to play.

        Args:
            max_time: Max time to come up with a move in seconds. Ignored.

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


class AutonomousAgent(Agent):

    """An AI agent that plays a given game.

    Attributes:
        player: Acting player.
    """

    def __init__(self, player, heuristics, transposition_table, searcher,
                 max_depth=None, resigns=True):
        """Constructs an AutonomousAgent.

        Args:
            player: Player to play as.
            heuristics: List of weighted heuristics to use.
            transposition_table: Transposition table.
            searcher: Searcher class to use.
            max_depth: Max depth to search for.
            resigns: Whether keyboard interrupts should be caught as
                resignations or not.
        """
        super().__init__(player)
        self._heuristics = heuristics
        self._transposition_table = transposition_table
        self._resigns = resigns
        self._searcher = searcher(player, heuristics, transposition_table,
                                  max_depth)

    def update(self, move):
        """Updates game with a given move.

        Args:
            move: Move.
        """
        super().update(move)

    def yield_move(self, max_time):
        """Yields a move to play.

        Args:
            max_time: Max time to come up with a move in seconds.

        Returns:
            Best available move so far.

        Raises:
            PlayerResigned: If the agent resigns.
        """
        print("Thinking... ")

        try:
            with timeout(max_time):
                self._searcher.search(self._game.to_game_state())
        except TimeoutError:
            pass
        except KeyboardInterrupt:
            if self._resigns:
                raise PlayerResigned
            raise KeyboardInterrupt

        move = self._searcher.request_move()
        print(move)

        return move

    def learn_from_mistakes(self):
        """Learns from its mistakes."""
        learner = Learner(self._root_board.copy(), self._game.moves,
                          self._heuristics, self._transposition_table)
        learner.learn()
