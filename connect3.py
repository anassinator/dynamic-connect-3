#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import argparse
import heuristics
from typing import List
from base_board import Player
from heuristics import WeightedHeuristic
from board import SmallBoard, LargeBoard
from agent import HumanAgent, AutonomousAgent
from game_connector import (GameConnector, LocalGameConnector,
                            RemoteGameConnector)


def _get_weighted_heuristics() -> List[WeightedHeuristic]:
    """Gets a list of weighted heuristics for an autonomous agent to use.

    Returns:
        List of weighted heuristics.
    """
    return [
        WeightedHeuristic(heuristics.GoalHeuristic, 100),
        WeightedHeuristic(heuristics.NumberOfRunsOfTwoHeuristic, 1),
        WeightedHeuristic(heuristics.DistanceToCenterHeuristic, 5),
        WeightedHeuristic(heuristics.NumberOfMovesHeuristic, 0.1),
        WeightedHeuristic(heuristics.NumberOfBlockedGoalsHeuristic, 10)
    ]


def player_vs_player(args) -> GameConnector:
    """Sets up connector to play a player vs player game.

    Args:
        args: Command-line arguments.

    Returns:
        Game connector.
    """
    white_agent = HumanAgent(Player.white)
    black_agent = HumanAgent(Player.black)
    return LocalGameConnector(white_agent, black_agent, args.max_time)


def player_vs_agent(args) -> GameConnector:
    """Sets up connector to play a player vs agent game.

    Args:
        args: Command-line arguments.

    Returns:
        Game connector.
    """
    weighted_heuristics = _get_weighted_heuristics()
    if args.player == Player.white:
        white_agent = HumanAgent(Player.white)
        black_agent = AutonomousAgent(Player.black, weighted_heuristics)
    elif args.player == Player.black:
        white_agent = AutonomousAgent(Player.white, weighted_heuristics)
        black_agent = HumanAgent(Player.black)
    else:
        raise NotImplementedError

    return LocalGameConnector(white_agent, black_agent, args.max_time)


def agent_vs_agent(args) -> GameConnector:
    """Sets up connector to play an agent vs agent game.

    Args:
        args: Command-line arguments.

    Returns:
        Game connector.
    """
    weighted_heuristics = _get_weighted_heuristics()
    white_agent = AutonomousAgent(Player.white, weighted_heuristics)
    black_agent = AutonomousAgent(Player.black, weighted_heuristics)
    return LocalGameConnector(white_agent, black_agent, args.max_time)


def play_vs_remote(args) -> GameConnector:
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
        agent = AutonomousAgent(args.player, _get_weighted_heuristics())
    return RemoteGameConnector(agent, args.max_time, args.id,
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

    # Player vs player play.
    pvp = subparsers.add_parser("pvp", help="play human vs human")
    add_shared_arguments(pvp)
    pvp.set_defaults(func=player_vs_player)

    # Player vs agent play.
    pve = subparsers.add_parser("pve", help="play human vs computer")
    add_shared_arguments(pve)
    pve.add_argument("--black", dest="player", const=Player.black,
                     default=Player.white, action="store_const",
                     help="play as black (default: white)")
    pve.set_defaults(func=player_vs_agent)

    # Agent vs agent play.
    agents = subparsers.add_parser("watch",
                                   help="watch the computer play itself")
    add_shared_arguments(agents)
    agents.set_defaults(func=agent_vs_agent)

    # Remote play.
    remote = subparsers.add_parser(
        "remote", help="play against a remote agent on a server")
    remote.add_argument("hostname", help="hostname of remote server")
    remote.add_argument("port", type=int, help="port of remote server")
    remote.add_argument("id", help="game ID")
    add_shared_arguments(remote)
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
