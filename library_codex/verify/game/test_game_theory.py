from fractions import Fraction

from library_codex.game.GameTheory import (
    ImpartialGameSolver,
    PartisanGameSolver,
    SurrealNumber,
)


def _fraction(value):
    return Fraction(value.numerator, 1 << value.exponent)


def test_surreal_arithmetic_children_and_between():
    values = [SurrealNumber(numerator, exponent)
              for exponent in range(7) for numerator in range(-30, 31)]
    for first in values:
        assert _fraction(-first) == -_fraction(first)
        left, right = first.children()
        assert left < first < right
        assert _fraction(left) < _fraction(first) < _fraction(right)
    for left in values[::17]:
        for right in values[::19]:
            if left < right:
                middle = SurrealNumber.between(left, right)
                assert left < middle < right


def test_impartial_solver_subtraction_and_split_games():
    options = lambda stones: [stones - take for take in (1, 2, 3)
                              if take <= stones]
    solver = ImpartialGameSolver(options)
    for stones in range(1000):
        assert solver.get(stones) == stones % 4

    def split_options(stones):
        return [[left, stones - 1 - left] for left in range(stones)]

    split = ImpartialGameSolver(split_options, splittable=True)
    for stones in range(50):
        reachable = {split.get(left) ^ split.get(stones - 1 - left)
                     for left in range(stones)}
        expected = 0
        while expected in reachable:
            expected += 1
        assert split.get(stones) == expected


def test_partisan_numeric_games_without_recursion():
    # Integer n is represented by {n-1 | } and negative n by { | n+1}.
    def options(value):
        if value > 0:
            return [value - 1], []
        if value < 0:
            return [], [value + 1]
        return [], []

    solver = PartisanGameSolver(options)
    for value in range(-1000, 1001):
        assert solver.get(value) == SurrealNumber(value)

    games = {
        "zero": ([], []),
        "half": (["zero"], ["one"]),
        "one": (["zero"], []),
    }
    solver = PartisanGameSolver(games.__getitem__)
    assert solver.get("half") == SurrealNumber(1, 1)
