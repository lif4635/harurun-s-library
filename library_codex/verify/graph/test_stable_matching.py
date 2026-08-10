from itertools import permutations
from random import Random

from library_codex.graph_matching.StableMatching import stable_matching


def _is_stable(first_preferences, second_preferences, match_first):
    second_count = len(second_preferences)
    match_second = [-1] * second_count
    for first, second in enumerate(match_first):
        if second != -1:
            match_second[second] = first
    first_rank = [
        {second: rank for rank, second in enumerate(order)}
        for order in first_preferences
    ]
    second_rank = [
        {first: rank for rank, first in enumerate(order)}
        for order in second_preferences
    ]
    for first, order in enumerate(first_preferences):
        current = match_first[first]
        current_rank = first_rank[first].get(current, len(order))
        for second in order[:current_rank]:
            if first not in second_rank[second]:
                continue
            other = match_second[second]
            if other == -1 or second_rank[second][first] < second_rank[second][other]:
                return False
    return True


def test_stable_matching_is_stable_with_incomplete_preferences():
    rng = Random(9021)
    for first_count in range(7):
        for second_count in range(7):
            for _ in range(30):
                first_preferences = []
                for _first in range(first_count):
                    order = list(range(second_count))
                    rng.shuffle(order)
                    first_preferences.append(order[:rng.randrange(second_count + 1)])
                second_preferences = []
                for _second in range(second_count):
                    order = list(range(first_count))
                    rng.shuffle(order)
                    second_preferences.append(order[:rng.randrange(first_count + 1)])
                match_first, match_second = stable_matching(
                    first_preferences, second_preferences
                )
                assert _is_stable(first_preferences, second_preferences, match_first)
                for first, second in enumerate(match_first):
                    if second != -1:
                        assert match_second[second] == first


def test_stable_matching_is_first_side_optimal_on_complete_instances():
    rng = Random(193)
    for n in range(1, 7):
        for _ in range(25):
            first_preferences = []
            second_preferences = []
            for _vertex in range(n):
                order = list(range(n))
                rng.shuffle(order)
                first_preferences.append(order)
                order = list(range(n))
                rng.shuffle(order)
                second_preferences.append(order)
            result, _ = stable_matching(first_preferences, second_preferences)
            stable = [
                order
                for order in permutations(range(n))
                if _is_stable(first_preferences, second_preferences, order)
            ]
            rank = [
                {second: position for position, second in enumerate(order)}
                for order in first_preferences
            ]
            for first in range(n):
                assert rank[first][result[first]] == min(
                    rank[first][order[first]] for order in stable
                )
