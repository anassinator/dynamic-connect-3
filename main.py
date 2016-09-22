#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from game import Game
from agent import Agent
from typing import List
from board import SmallBoard
from base_board import Board, Player
from abc import ABCMeta, abstractmethod
from move import Move, InvalidMove, PlayerResigned
from heuristics import WeightedHeuristic, GoalHeuristic, NumberOfRunsOfTwoHeuristic


class GameConnector(object, metaclass=ABCMeta):

    """Game connector."""

    async def start(self, board: Board):
        """Starts a game asynchronously.

        Args:
            board: Board to start with.
        """
        game = Game(board)

        while game.turn != Player.none:
            self.on_turn(game.board, game.turn)

            try:
                move = await self.yield_move(game.board, game.turn)
                game.play(move)
            except PlayerResigned:
                self.on_resignation(game.turn)
                break
            except InvalidMove as e:
                self.on_invalid_move(e.message)
                continue

        if game.won != Player.none:
            self.on_win(game.won)
        elif game.draw:
            self.on_draw()

    @abstractmethod
    async def yield_move(self, board: Board, turn: Player) -> Move:
        """Yields a move for the given player to play.
        
        Args:
            board: Board to play on.
            turn: Turn to play.

        Returns:
            A move to play.

        Raises:
            PlayerResigned: On player's resignation.
        """
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

    def on_win(self, player: Player):
        """Called when the game was won.

        Args:
            player: Player who win.
        """
        print(board)
        print("{} wins.".format(player.name.capitalize()))

    def on_draw(self):
        """Called when the game ends in a draw."""
        print(board)
        print("Draw.")


class PlayerVsPlayerGameConnector(GameConnector):

    """Player vs player game connector."""

    async def yield_move(self, board: Board, turn: Player) -> Move:
        """Yields a move for the given player to play.

        Args:
            board: Board to play on.
            turn: Turn to play.

        Returns:
            A move to play.

        Raises:
            PlayerResigned: On player's resignation.
        """
        try:
            s = input("Enter a move: ")
            return Move.from_str(s)
        except (KeyboardInterrupt, EOFError):
            raise PlayerResigned


class PlayerVsAgentGameConnector(PlayerVsPlayerGameConnector):

    """Player vs agent game connector."""

    def __init__(self, player: Player, heuristics: List[WeightedHeuristic]):
        """Constructs a PlayerVsAgentGameConnector.

        Args:
            player: Player for the agent to play as.
            heuristics: List of weighted heuristics to use.
        """
        self._agent_player = player
        self._heuristics = heuristics

    async def start(self, board: Board):
        """Starts a game asynchronously.

        Args:
            board: Board to start with.
        """
        self._agent = Agent(board, self._agent_player, self._heuristics)
        await super().start(board)

    async def yield_move(self, board: Board, turn: Player) -> Move:
        """Yields a move for the given player to play.

        Args:
            board: Board to play on.
            turn: Turn to play.

        Returns:
            A move to play.

        Raises:
            PlayerResigned: On player's resignation.
        """
        if turn == self._agent_player:
            print("Thinking... ", end="")
            move = self._agent.request_move()
            print(move)
        else:
            move = await super().yield_move(board, turn)
        self._agent.update_state(move, Player(1 - turn.value))
        return move


class AgentVsAgentGameConnector(GameConnector):

    """Agent vs agent game connector."""

    def __init__(self, white_heuristics: List[WeightedHeuristic],
                 black_heuristics: List[WeightedHeuristic]):
        """Constructs a AgentVsAgentGameConnector.

        Args:
            white_heuristics: List of weighted heuristics to use by the white
                player.
            black_heuristics: List of weighted heuristics to use by the black
                player.
        """
        self._white_heuristics = white_heuristics
        self._black_heuristics = black_heuristics

    async def start(self, board: Board):
        """Starts a game asynchronously.

        Args:
            board: Board to start with.
        """
        self._white_agent = Agent(board, Player.white, self._white_heuristics)
        self._black_agent = Agent(board, Player.black, self._black_heuristics)
        await super().start(board)

    async def yield_move(self, board: Board, turn: Player) -> Move:
        """Yields a move for the given player to play.

        Args:
            board: Board to play on.
            turn: Turn to play.

        Returns:
            A move to play.

        Raises:
            PlayerResigned: On player's resignation.
        """
        print("Thinking... ", end="")
        if turn == Player.white:
            move = self._white_agent.request_move()
        else:
            move = self._black_agent.request_move()

        print(move)
        opponent = Player(1 - turn.value)
        self._white_agent.update_state(move, opponent)
        self._black_agent.update_state(move, opponent)
        return move


if __name__ == "__main__":
    board = SmallBoard()
    heuristics = [
        WeightedHeuristic(GoalHeuristic, 1),
        WeightedHeuristic(NumberOfRunsOfTwoHeuristic, 1)
    ]

    connector = AgentVsAgentGameConnector(heuristics, heuristics)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(connector.start(board))
    loop.close()
