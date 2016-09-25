# -*- coding: utf-8 -*-

import sys
import asyncio
from game import Game
from typing import Type
from agent import Agent
from base_board import Board, Player
from abc import ABCMeta, abstractmethod
from move import Move, InvalidMove, PlayerResigned


class GameConnector(object, metaclass=ABCMeta):

    """Game connector."""

    def __init__(self):
        """Constructs a GameConnector."""
        self._winner = Player.none

    @property
    def winner(self) -> Player:
        """Returns the winner of the game."""
        return self._winner

    @asyncio.coroutine
    def start(self, board_class: Type[Board]):
        """Starts a game asynchronously.

        Args:
            board_class: Game board type to start with.
        """
        game = Game(board_class())
        yield from self.setup(game)

        while game.turn != Player.none:
            self.on_turn(game.board, game.turn)

            try:
                move = yield from self.request_move(game.turn)
                game.play(move)
            except PlayerResigned:
                self.on_resignation(game.turn)
                break
            except InvalidMove as e:
                self.on_invalid_move(e.message)
                continue

            yield from self.on_successful_move(move)

        if game.won != Player.none:
            self._winner = game.won
            self.on_win(game.board, game.won)
        elif game.draw:
            self.on_draw(game.board)

        yield from self.teardown()

    @abstractmethod
    @asyncio.coroutine
    def setup(self, game: Game):
        """Sets up game before it starts.

        Args:
            game: Game to play.
        """
        raise NotImplementedError

    @abstractmethod
    @asyncio.coroutine
    def teardown(self):
        """Tears down game once it ends."""
        raise NotImplementedError

    @abstractmethod
    @asyncio.coroutine
    def request_move(self, turn: Player) -> Move:
        """Requests a move from the given player.

        Args:
            player: Player's turn.

        Returns:
            Move.
        """
        raise NotImplementedError

    @abstractmethod
    @asyncio.coroutine
    def on_successful_move(self, move: Move):
        """Called when a move has been validated.

        Should be used to update the game state.

        Args:
            move: Move played.
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


class LocalGameConnector(GameConnector):

    """Local multi-agent game connector."""

    def __init__(self, white_agent: Agent, black_agent: Agent,
                 max_time: int):
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

        super().__init__()

    @asyncio.coroutine
    def setup(self, game: Game):
        """Sets up game before it starts.

        Args:
            game: Game to play.
        """
        self._white_agent.play(game.copy())
        self._black_agent.play(game.copy())

    @asyncio.coroutine
    def teardown(self):
        """Tears down game once it ends."""
        pass

    @asyncio.coroutine
    def request_move(self, turn: Player) -> Move:
        """Requests a move from the given player.

        Args:
            turn: Player's turn.

        Returns:
            Move.
        """
        if turn == Player.white:
            return self._white_agent.yield_move(self._max_time)
        elif turn == Player.black:
            return self._black_agent.yield_move(self._max_time)
        else:
            raise NotImplementedError

    @asyncio.coroutine
    def on_successful_move(self, move: Move):
        """Called when a move has been validated.

        Args:
            move: Move played.
        """
        self._white_agent.update(move)
        self._black_agent.update(move)


class RemoteGameConnector(GameConnector):

    """Remote game connector."""

    BUFFERSIZE = 1024

    def __init__(self, agent: Agent, max_time: int, game_id: str,
                 hostname: str, port: int, loop: asyncio.AbstractEventLoop):
        """Constructs a RemoteGameConnector using given agent as a local player..

        Args:
            agent: Black agent.
            max_time: Max time for an agent to come up with a move in seconds.
            game_id: Remote game ID.
            hostname: Hostname of remote server.
            port: Port of remote server.
            loop: Event loop.
        """
        self._agent = agent
        self._max_time = max_time

        self._game_id = game_id
        self._hostname = hostname
        self._port = port
        self._loop = loop

        self._reader = None
        self._writer = None

        super().__init__()

    @asyncio.coroutine
    def setup(self, game: Game):
        """Sets up game before it starts.

        Args:
            game: Game to play.
        """
        self._agent.play(game.copy())

        print("Connecting... ", end="")
        sys.stdout.flush()

        # Connect to remote server.
        transport = yield from asyncio.open_connection(self._hostname,
                                                       self._port,
                                                       loop=self._loop)
        self._reader, self._writer = transport

        # Write header to connect to and start game.
        header = "{} {}\n".format(self._game_id, self._agent.player.name)
        self._writer.write(header.encode())
        yield from self._reader.read(self.BUFFERSIZE)
        print("OK")

    @asyncio.coroutine
    def teardown(self):
        """Tears down game once it ends."""
        if self._writer:
            self._writer.close()

        self._writer = None
        self._reader = None

    @asyncio.coroutine
    def request_move(self, turn: Player) -> Move:
        """Requests a move from the given player.

        Args:
            turn: Player's turn.

        Returns:
            Move.
        """
        if turn == self._agent.player:
            move = self._agent.yield_move(self._max_time)

            # Forward agent's move to the server.
            encoded_move = "{}\n".format(move).encode()
            self._writer.write(encoded_move)
            yield from self._reader.read(self.BUFFERSIZE)
        else:
            encoded_move = None
            while True:
                print("Waiting for move... ", end="")
                sys.stdout.flush()
                encoded_move = yield from self._reader.read(self.BUFFERSIZE)
                if encoded_move is None or len(encoded_move) == 0:
                    print("Received empty response: {}".format(encoded_move))
                    yield from asyncio.sleep(1)
                    continue

            try:
                move = Move.from_str(encoded_move.decode().strip())
                print(move)
            except InvalidMove as e:
                print("{}: {} ({} bytes)".format(e.message,
                                                 encoded_move,
                                                 len(encoded_move)))
                raise PlayerResigned

        return move

    @asyncio.coroutine
    def on_successful_move(self, move: Move):
        """Called when a move has been validated.

        Args:
            move: Move played.
        """
        self._agent.update(move)
