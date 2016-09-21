#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from game import Game
from board import SmallBoard
from base_board import Board, Player
from abc import ABCMeta, abstractmethod
from move import Move, InvalidMove, PlayerResigned


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
        print("{} wins.".format(player.name.capitalize()))

    def on_draw(self):
        """Called when the game ends in a draw."""
        print("Draw.")


class PvPGameConnector(GameConnector):

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
            s = "{}'s turn. Enter a move: ".format(turn.name.capitalize())
            return Move.from_str(input(s))
        except (KeyboardInterrupt, EOFError):
            raise PlayerResigned


if __name__ == "__main__":
    board = SmallBoard()
    connector = PvPGameConnector()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(connector.start(board))
    loop.close()
