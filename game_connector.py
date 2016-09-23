# -*- coding: utf-8 -*-

import asyncio
from game import Game
from typing import Type
from agent import Agent
from base_board import Board, Player
from move import InvalidMove, PlayerResigned


class GameConnector(object):

    """Game connector."""

    def __init__(self, white_agent: Agent, black_agent: Agent,
                 max_time: float):
        """Constructs a GameConnector from two opposing agents.
        
        Args:
            white_agent: White agent.
            black_agent: Black agent.
            max_time: Max time for an agent to come up with a move in seconds.
        """
        self._white_agent = white_agent
        self._black_agent = black_agent
        self._max_time = max_time

        if white_agent.player == black_agent.player:
            player = white_agent.player
            raise Exception("Both players cannot be {}.".format(player))

    async def start(self, board_class: Type[Board]):
        """Starts a game asynchronously.
        
        Args:
            board_class: Game board type to start with.
        """
        game = Game(board_class())

        self._white_agent.play(game.copy())
        self._black_agent.play(game.copy())

        while game.turn != Player.none:
            self.on_turn(game.board, game.turn)
            current = self._get_current_player(game.turn)

            try:
                move = current.yield_move(self._max_time)
                game.play(move)
            except PlayerResigned:
                self.on_resignation(game.turn)
                break
            except InvalidMove as e:
                self.on_invalid_move(e.message)
                continue

            self._white_agent.update(move)
            self._black_agent.update(move)

        if game.won != Player.none:
            self.on_win(game.board, game.won)
        elif game.draw:
            self.on_draw(game.board)

    def _get_current_player(self, turn: Player) -> Player:
        """Returns the agent corresponding to the current turn.

        Args:
            turn: Player's turn.

        Returns:
            Current agent.
        """
        if turn == Player.white:
            return self._white_agent
        elif turn == Player.black:
            return self._black_agent
        else:
            raise NotImplementedError

    def on_invalid_move(self, msg: str):
        """Called when an invalid move is played.
        
        Args:
            msg: Why the move was invalid.
        """
        print(msg)

    def on_turn(self, board: Board, turn: Player):
        """Called when a player must make a move.

        Args:
            board: Board to play on.
            turn: Turn to play.
        """
        print(board)
        print("{}'s turn.".format(turn.name.capitalize()))

    def on_resignation(self, player: Player):
        """Called when a player resigns.

        Args:
            player: Player who resigned.
        """
        print("{} resigned.".format(player.name.capitalize()))

    def on_win(self, board: Board, player: Player):
        """Called when the game was won.

        Args:
            board: Current board.
            player: Player who win.
        """
        print(board)
        print("{} wins.".format(player.name.capitalize()))

    def on_draw(self, board: Board):
        """Called when the game ends in a draw.
        
        Args:
            board: Current board.
        """
        print(board)
        print("Draw.")
