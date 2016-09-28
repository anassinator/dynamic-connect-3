#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import argparse
import itertools
import heuristics
import transposition_table
from base_board import Player
from collections import Counter
from heuristics import WeightedHeuristic
from board import SmallBoard, LargeBoard
from agent import HumanAgent, AutonomousAgent
from search import AlphaBetaPrunedMinimaxSearch, MinimaxSearch
from game_connector import LocalGameConnector, RemoteGameConnector


def _get_searcher(args):
    """Gets a searcher.

    Args:
        args: Command-line arguments.

    Returns:
        Searcher to use.
    """
    if args.no_alpha_beta:
        return MinimaxSearch
    return AlphaBetaPrunedMinimaxSearch


def _get_transposition_table(args):
    """Gets transposition table to use.

    Args:
        args: Command-line arguments.

    Returns:
        TranspositionTable.
    """
    if args.no_table:
        return transposition_table.EmptyTranspositionTable()

    if args.no_db:
        return transposition_table.TemporaryTranspositionTable()

    filename = "connect3_small.db"
    if args.board == LargeBoard:
        filename = "connect3_large.db"
    if args.db:
        filename = args.db

    return transposition_table.PermanentTranspositionTable(filename)


def _get_weighted_heuristics(args):
    """Gets a list of weighted heuristics for an autonomous agent to use.

    Args:
        args: Command-line arguments.

    Returns:
        List of weighted heuristics.
    """
    wh = [
        WeightedHeuristic(heuristics.GoalHeuristic, 100),
        WeightedHeuristic(heuristics.DistanceToCenterHeuristic, 5),
        WeightedHeuristic(heuristics.NumberOfRunsOfTwoHeuristic, 1)
    ]

    if args.random:
        wh.append(WeightedHeuristic(heuristics.RandomHeuristic, 0.1))

    return wh


def player_vs_player(args):
    """Sets up connector to play a player vs player game.

    Args:
        args: Command-line arguments.

    Returns:
        Game connector.
    """
    white_agent = HumanAgent(Player.white)
    black_agent = HumanAgent(Player.black)
    return LocalGameConnector(white_agent, black_agent, args.max_time, False)


def player_vs_agent(args):
    """Sets up connector to play a player vs agent game.

    Args:
        args: Command-line arguments.

    Returns:
        Game connector.
    """
    weighted_heuristics = _get_weighted_heuristics(args)
    transposition_table = _get_transposition_table(args)
    searcher = _get_searcher(args)
    if args.player == Player.white:
        white_agent = HumanAgent(Player.white)
        black_agent = AutonomousAgent(Player.black, weighted_heuristics,
                                      transposition_table, searcher,
                                      args.max_depth)
    elif args.player == Player.black:
        white_agent = AutonomousAgent(Player.white, weighted_heuristics,
                                      transposition_table, searcher,
                                      args.max_depth)
        black_agent = HumanAgent(Player.black)
    else:
        raise NotImplementedError

    return LocalGameConnector(white_agent, black_agent, args.max_time, False)


def agent_vs_agent(args):
    """Sets up connector to play an agent vs agent game.

    Args:
        args: Command-line arguments.

    Returns:
        Game connector.
    """
    weighted_heuristics = _get_weighted_heuristics(args)
    transposition_table = _get_transposition_table(args)
    searcher = _get_searcher(args)
    white_agent = AutonomousAgent(Player.white, weighted_heuristics,
                                  transposition_table, searcher,
                                  args.max_depth)
    black_agent = AutonomousAgent(Player.black, weighted_heuristics,
                                  transposition_table, searcher,
                                  args.max_depth)
    return LocalGameConnector(white_agent, black_agent, args.max_time,
                              args.learn)


def train(args):
    """Sets up connector to train two agents forever.

    Args:
        args: Command-line arguments.

    Returns:
        Game connector.
    """
    weighted_heuristics = _get_weighted_heuristics(args)
    transposition_table = _get_transposition_table(args)
    searcher = _get_searcher(args)

    class TrainingGameConnector(object):

        """Training game connector."""

        @asyncio.coroutine
        def start(self, board_class):
            """Starts a game asynchronously.

            Args:
                board_class: Game board type to start with.
            """
            max_time = args.max_time
            winners = Counter()

            try:
                for game_num in itertools.count(1):
                    print("Starting game #{}.".format(game_num))
                    white_agent = AutonomousAgent(Player.white,
                                                  weighted_heuristics,
                                                  transposition_table,
                                                  searcher, args.max_depth,
                                                  False)
                    black_agent = AutonomousAgent(Player.black,
                                                  weighted_heuristics,
                                                  transposition_table,
                                                  searcher, args.max_depth,
                                                  False)
                    connector = LocalGameConnector(white_agent, black_agent,
                                                   max_time, args.learn)
                    yield from connector.start(board_class)

                    winners.update([connector.winner])

                    if connector.winner == Player.none:
                        max_time += 1
                        print("Increasing max time to {} seconds."
                              .format(max_time))
            except KeyboardInterrupt:
                print("Played {} games with up to {} seconds per move."
                      .format(game_num, max_time))
                for player in winners:
                    if player == Player.none:
                        print("Draw: {}".format(winners[player]))
                    else:
                        print("{} won:".format(player.name.capitalize(),
                                               winners[player]))
                return

    return TrainingGameConnector()


def play_vs_remote(args):
    """Sets up connector to play a game vs a remote agent.

    Args:
        args: Command-line arguments.

    Returns:
        Game connector.
    """
    loop = asyncio.get_event_loop()
    if args.human:
        agent = HumanAgent(args.player)
    else:
        agent = AutonomousAgent(args.player, _get_weighted_heuristics(args),
                                _get_transposition_table(args),
                                _get_searcher(args), args.max_depth)
    return RemoteGameConnector(agent, args.max_time, args.learn, args.id,
                               args.hostname, args.port, loop)


def parse_args():
    """Parses command line arguments.

    Returns:
        Command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Play Dynamic Connect-3")
    subparsers = parser.add_subparsers()

    def add_shared_arguments(subparser):
        subparser.add_argument("--large", dest="board", default=SmallBoard,
                               const=LargeBoard, action="store_const",
                               help="play on larger 7x6 board")
        subparser.add_argument("--max-time", default=9, type=int,
                               help="max time to make a move in seconds")

    def add_agent_arguments(subparser):
        subparser.add_argument("--no-table", default=False,
                               action="store_true",
                               help="don't use a transposition table")
        subparser.add_argument("--no-alpha-beta", default=False,
                               action="store_true",
                               help="don't use alpha-beta pruning")
        subparser.add_argument("--max-depth", default=None, type=int,
                               help="limit search depth")
        subparser.add_argument("--no-db", default=False, action="store_true",
                               help="do not use database to speed things up")
        subparser.add_argument("--db", default=None,
                               help="use custom database")
        subparser.add_argument("--no-learn", dest="learn", default=True,
                               action="store_false",
                               help="don't learn from mistakes")
        subparser.add_argument("--random", default=False, action="store_true",
                               help="randomly choose between equivalent moves")

    # Player vs player play.
    pvp = subparsers.add_parser("pvp", help="play human vs human")
    add_shared_arguments(pvp)
    pvp.set_defaults(func=player_vs_player)

    # Player vs agent play.
    pve = subparsers.add_parser("pve", help="play human vs computer")
    add_shared_arguments(pve)
    add_agent_arguments(pve)
    pve.add_argument("--black", dest="player", const=Player.black,
                     default=Player.white, action="store_const",
                     help="play as black (default: white)")
    pve.set_defaults(func=player_vs_agent)

    # Agent vs agent play.
    agents = subparsers.add_parser("watch",
                                   help="watch the computer play itself")
    add_shared_arguments(agents)
    add_agent_arguments(agents)
    agents.set_defaults(func=agent_vs_agent)

    training = subparsers.add_parser("train",
                                     help="train agents until interrupted")
    add_shared_arguments(training)
    add_agent_arguments(training)
    training.set_defaults(func=train)

    # Remote play.
    remote = subparsers.add_parser(
        "remote", help="play against a remote agent on a server")
    remote.add_argument("hostname", help="hostname of remote server")
    remote.add_argument("port", type=int, help="port of remote server")
    remote.add_argument("id", help="game ID")
    add_shared_arguments(remote)
    add_agent_arguments(remote)
    remote.add_argument("--black", dest="player", const=Player.black,
                        default=Player.white, action="store_const",
                        help="play as black (default: white)")
    remote.add_argument("--human", default=False, action="store_true",
                        help="play as human")
    remote.set_defaults(func=play_vs_remote)

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    connector = args.func(args)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(connector.start(args.board))
    loop.close()
