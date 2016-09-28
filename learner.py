# -*- coding: utf-8 -*-

from game import Game
from base_board import Player


class Learner(object):

    """Learns from a game to find mistakes and unavoidable pitfalls."""

    def __init__(self, root_board, moves, weighted_heuristics,
                 transposition_table, winner):
        """Constructs a Learner.

        Args:
            root_board: Root board game started from.
            moves: Ordered list of moves played.
            weighted_heuristics: List of weighted heuristics to use.
            transposition_table: Transposition table.
            winner: Player who won.
        """
        self._root_board = root_board
        self._moves = moves
        self._heuristics = weighted_heuristics
        self._transposition_table = transposition_table
        self._winner = winner
        self._loser = Player(1 - winner.value)

    def learn(self):
        """Learns."""
        print("Looking for mistakes...")

        # Backtrack through game states until we find the first mistake.
        first_unavoidable_death = None
        game_states = list(self._all_game_states())
        for i, state in reversed(list(enumerate(game_states))):
            if state.turn == self._loser and i > 0:
                if self._is_mistake(state):
                    first_unavoidable_death = i
                    print("Found unavoidable death at state: {}, turn: {}"
                          .format(i, state.turn.name))
                    print(state.board)

        # Find cause and fix its heuristic.
        if first_unavoidable_death and first_unavoidable_death > 0:
            mistake = first_unavoidable_death - 1

            cause = game_states[mistake]
            effect = game_states[first_unavoidable_death]

            print("Found mistake at move: {}, {}"
                  .format(mistake, self._moves[mistake]))
            print(cause.board)

            cause_heuristic = self._transposition_table[(cause, 0)]
            effect_heuristic = self._transposition_table[(effect, 0)]

            print("Heuristic at effect: {}".format(effect_heuristic))
            print("Previous cause heuristic: {}".format(cause_heuristic))

            new_heuristic = effect_heuristic / 2
            if new_heuristic == cause_heuristic:
                new_heuristic = effect_heuristic

            print("Setting heuristic to: {}".format(new_heuristic))
            self._transposition_table._update_heuristic(cause, new_heuristic)
        else:
            print("Found no mistakes :)")

    def _is_mistake(self, state):
        """Returns whether the current state leads to an unavoidable loss or
        not.

        Args:
            state: State.

        Returns:
            Whether the given state certainly leads to an unavoidable loss to
            the current player's turn or not.
        """
        for move, child in state.next_states():
            v = self._transposition_table[(child, 0)]
            if state.turn == Player.white:
                if v > -1000:
                    return False
            elif state.turn == Player.black:
                if v < 1000:
                    return False

        return True

    def _all_game_states(self):
        """Yields ordered list of game states as they were played."""
        game = Game(self._root_board)
        yield game.to_game_state()

        for move in self._moves:
            game.play(move)
            yield game.to_game_state()
