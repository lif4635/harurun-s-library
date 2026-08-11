import itertools
import random

import pytest

from library_codex.graph_matching.StableRoommates import stable_roommates


def _stable(preferences, partner):
    rank = [{other: index for index, other in enumerate(row)} for row in preferences]
    for first in range(len(partner)):
        if partner[partner[first]] != first or partner[first] == first:
            return False
        for second in range(first + 1, len(partner)):
            if partner[first] == second:
                continue
            if (rank[first][second] < rank[first][partner[first]]
                    and rank[second][first] < rank[second][partner[second]]):
                return False
    return True


def _matchings(vertices):
    stack = [([], vertices)]
    while stack:
        pairs, remaining = stack.pop()
        if not remaining:
            yield pairs
            continue
        first = remaining[0]
        for index in range(len(remaining) - 1, 0, -1):
            second = remaining[index]
            rest = remaining[1:index] + remaining[index + 1:]
            stack.append((pairs + [(first, second)], rest))


def _brute(preferences):
    n = len(preferences)
    for pairs in _matchings(list(range(n))):
        partner = [-1] * n
        for first, second in pairs:
            partner[first] = second
            partner[second] = first
        if _stable(preferences, partner):
            return partner
    return None


def test_random_against_all_perfect_matchings():
    random.seed(20260819)
    for n in (2, 4, 6, 8):
        for _ in range(180 if n < 8 else 80):
            preferences = []
            for person in range(n):
                row = [other for other in range(n) if other != person]
                random.shuffle(row)
                preferences.append(row)
            expected = _brute(preferences)
            result = stable_roommates(preferences)
            assert (result is None) == (expected is None)
            if result is not None:
                assert _stable(preferences, result)


def test_boundaries_and_validation():
    assert stable_roommates([]) == []
    assert stable_roommates([[1], [0]]) == [1, 0]
    assert stable_roommates([[1, 2], [0, 2], [0, 1]]) is None
    with pytest.raises(ValueError):
        stable_roommates([[1, 1], [0, 2], [0, 1], [0, 1, 2]])
