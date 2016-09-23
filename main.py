#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from board import SmallBoard
from base_board import Player
from typing import List, Tuple
from game_connector import GameConnector
from agent import Agent, HumanAgent, AutonomousAgent
from heuristics import (WeightedHeuristic, GoalHeuristic,
                        NumberOfRunsOfTwoHeuristic)


def get_weighted_heuristics() -> List[WeightedHeuristic]:
    """Gets a list of weighted heuristics for an autonomous agent to use.

    Returns:
        List of weighted heuristics.
    """
    return [
        WeightedHeuristic(GoalHeuristic, 1),
        WeightedHeuristic(NumberOfRunsOfTwoHeuristic, 1)
    ]


def player_vs_player() -> Tuple[Agent, Agent]:
    """Sets up agents to play a player vs player game.

    Returns:
        Tuple of (white agent, black agent).
    """
    white_agent = HumanAgent(Player.white)
    black_agent = HumanAgent(Player.black)
    return (white_agent, black_agent)


def player_vs_agent(human: Player=Player.white) -> Tuple[Agent, Agent]:
    """Sets up agents to play a player vs agent game.

    Args:
        human: Player for human to play as.

    Returns:
        Tuple of (white agent, black agent).
    """
    weighted_heuristics = get_weighted_heuristics()
    if human == Player.white:
        white_agent = HumanAgent(Player.white)
        black_agent = AutonomousAgent(Player.black, weighted_heuristics)
    elif human == Player.black:
        white_agent = AutonomousAgent(Player.white, weighted_heuristics)
        black_agent = HumanAgent(Player.black)
    else:
        raise NotImplementedError

    return (white_agent, black_agent)


def agent_vs_agent():
    """Sets up agents to play an agent vs agent game.

    Returns:
        Tuple of (white agent, black agent).
    """
    weighted_heuristics = get_weighted_heuristics()
    white_agent = AutonomousAgent(Player.white, weighted_heuristics)
    black_agent = AutonomousAgent(Player.black, weighted_heuristics)
    return (white_agent, black_agent)


if __name__ == "__main__":
    board = SmallBoard
    timeout = 3

    white_agent, black_agent = agent_vs_agent()
    connector = GameConnector(white_agent, black_agent, timeout)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(connector.start(board))
    loop.close()
