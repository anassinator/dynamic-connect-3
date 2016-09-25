# -*- coding: utf-8 -*-

import random
import asyncio
import heuristics
from board import SmallBoard
from typing import List, Tuple
from agent import AutonomousAgent
from base_board import Board, Player
from game_connector import LocalGameConnector
from heuristics import Heuristic, WeightedHeuristic


def generate_random_heuristics(heuristics: List[Heuristic]):
    """Generates a list of heuristics with random weights.

    Args:
        heuristics: Heuristics to choose from.

    Returns:
        List of randomly weighted heuristics.
    """
    weighted_heuristics = []
    for h in heuristics:
        weight = random.random()
        weighted_heuristics.append(WeightedHeuristic(h, weight))

    return weighted_heuristics


def perturb(weighted_heuristics: List[WeightedHeuristic], prob: float):
    child = []
    for wh in weighted_heuristics:
        weight = wh.weight
        if prob > random.random():
            weight = random.random()
        child.append(WeightedHeuristic(wh.heuristic, weight))

    return child


@asyncio.coroutine
def play(white_heuristics: List[WeightedHeuristic],
         black_heuristics: List[WeightedHeuristic],
         board: Board, max_time: int) -> Player:
    white_agent = AutonomousAgent(Player.white, white_heuristics)
    black_agent = AutonomousAgent(Player.black, black_heuristics)
    connector = LocalGameConnector(white_agent, black_agent, max_time)
    yield from connector.start(board)
    return connector.winner


def _format_heuristics(weighted_heuristics: List[WeightedHeuristic]):
    return [(wh.heuristic.__name__, wh.weight)
            for wh in weighted_heuristics]

@asyncio.coroutine
def climb(first_heuristics: List[WeightedHeuristic],
          second_heuristics: List[WeightedHeuristic],
          board: Board, generations: int=100, perturbations: float=0.25):

    first_child = first_heuristics
    second_child = second_heuristics

    first_wins_most = [
        (Player.white, Player.black),
        (Player.white, Player.none),
        (Player.none, Player.black)
    ]

    second_wins_most = [
        (Player.black, Player.white),
        (Player.black, Player.none),
        (Player.none, Player.black)
    ]

    max_time = 1
    try:
        for gen in range(generations):
            print("First child: {}".format(_format_heuristics(first_child)))
            print("Second child: {}".format(_format_heuristics(second_child)))

            print("Playing first game...")
            first_winner = yield from play(first_child, second_child,
                                           board, max_time)

            print("Playing second game...")
            second_winner = yield from play(first_child, second_child,
                                            board, max_time)

            results = (first_winner, second_winner)

            if results in first_wins_most:
                # First child won most times so improve his opponent.
                second_child = perturb(first_child, perturbations)
                print("First child won: {}".format(results))
            elif results in second_wins_most:
                # Second child won most times so improve his opponent.
                # Also rank them such that first child is always the best.
                first_child = second_child
                second_child = perturb(second_child, perturbations)
                print("Second child won: {}".format(results))
            else:
                # Draw so play again but increase the thought time this time.
                max_time += 1
                print("Draw. Playing again with {} seconds".format(max_time))
    except KeyboardInterrupt:
        print(_format_heuristics(first_child))
        return

    print(_format_heuristics(first_child))


if __name__ == "__main__":
    all_heuristics = [
        heuristics.DistanceToCenterHeuristic,
        heuristics.DistanceToGoalHeuristic,
        heuristics.GoalHeuristic,
        heuristics.NumberOfBlockedGoalsHeuristic,
        heuristics.NumberOfMovesHeuristic,
        heuristics.NumberOfRunsOfTwoHeuristic,
        heuristics.TurnHeuristic
    ]

    first_heuristics = generate_random_heuristics(all_heuristics)
    second_heuristics = generate_random_heuristics(all_heuristics)

    board = SmallBoard

    loop = asyncio.get_event_loop()
    loop.run_until_complete(climb(first_heuristics, second_heuristics, board))
    loop.close()
