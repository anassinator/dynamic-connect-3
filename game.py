#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from move import InvalidMove
from base_board import Player
from draw_tracker import DrawTracker


class GameState(object):

    """Game state."""

    def __init__(self, board, turn):
        """Constructs a GameState.

        Args:
            board: Board.
            turn: Player's turn.
        """
        self.board = board
        self.turn = turn
        self._next_turn = (Player.black if turn == Player.white else
                           Player.white)

    def __eq__(self, other):
        """Returns whether two game states are equal or not.

        Args:
            other: Game state to compare to.

        Returns:
            Whether the two game states are equivalent or not.
        """
        return (self.board._white_pieces == other.board._white_pieces and
                self.board._black_pieces == other.board._black_pieces and
                self.turn == other.turn)

    def __hash__(self):
        """Hashes the current game state into a unique integer.

        Returns:
            Hashed value.
        """
        return hash((self.board._white_pieces,
                     self.board._black_pieces,
                     self.turn))

    def compute_heuristic(self, weighted_heuristics):
        """Computes the weighted heuristic for the game state given.

        Args:
            weighted_heuristics: List of weighted heuristics.

        Returns:
            The estimated value of the board such that the more positive it is
            the more in favor of the white player the board is and the more
            negative it is, the more in favor of the black player the board is.
            This is effectively a weighted sum of all the heuristics this agent
            considers.
        """
        heuristic = 0
        for wh in weighted_heuristics:
            v = wh.heuristic.compute(self.board, self.turn)
            heuristic += wh.weight * v
        return heuristic

    def won_by(self):
        """Returns who won the current game state."""
        if self.board.is_goal(Player.white):
            return Player.white
        elif self.board.is_goal(Player.black):
            return Player.black
        else:
            return Player.none

    def next_states(self):
        """Yields all possible next states.

        Yields:
            Tuple of (move, resulting game state).
        """
        for move in self.board.available_moves(self.turn):
            child_board = self.board.copy()
            child_board.move(move)
            yield (move, GameState(child_board, self._next_turn))

    def copy(self):
        """Returns a copy of the game state."""
        return GameState(self.board.copy(), self.turn)



class Game(object):

    """A game instance.

    Attributes:
        board: Current board state.
        draw: Whether the game ended in a draw or not.
        turn: Current player.
        won: Which player won.
    """

    def __init__(self, board, draw_tracker=None):
        """Constructs a Game instance from a given starting position.

        Args:
            board: Starting board position.
            draw_tracker: Draw tracker to start with.
        """
        self.board = board
        self.turn = Player.white
        self.won = Player.none
        self.draw = False
        self.moves = []

        if draw_tracker is None:
            self._draw_tracker = DrawTracker()
            self._draw_tracker.update(self.board, self.turn)
        else:
            self._draw_tracker = draw_tracker

    def play(self, move):
        """Plays a given move and switches to next player's turn.

        Args:
            move: Move to play.
        """
        # Make sure it's the correct person's move.
        # Empty cells raise an InvalidMove in self.board.move so deal with it
        # there.
        if self.board.get(move.x, move.y) not in (self.turn, Player.none):
            raise InvalidMove("Not your turn")

        self.board.move(move)
        self.moves.append(move)

        if self.board.is_goal(self.turn):
            self.won = self.turn

        self.turn = Player(not self.turn.value)
        self.draw = self._draw_tracker.update(self.board, self.turn)

        if self.won != Player.none or self.draw:
            self.turn = Player.none

    def copy(self):
        """Returns a deep copy of the game.

        Returns:
            A copy of the current game state.
        """
        game = Game(self.board.copy(), self._draw_tracker.copy())
        game.turn = self.turn
        game.won = self.won
        game.draw = self.draw
        return game

    def to_game_state(self):
        """Returns the equivalent game state."""
        return GameState(self.board.copy(), self.turn)
