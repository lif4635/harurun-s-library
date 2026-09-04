import random

from library_codex.optimization.MonotoneConvexHullTrick import (
    MonotoneConvexHullTrick,
)


def test_monotone_cht_all_directions_and_objectives():
    rng = random.Random(187349)
    for minimize in (False, True):
        for increasing in (False, True):
            for _ in range(500):
                slopes = sorted(set(rng.randrange(-1000, 1001) for _ in range(100)))
                if not increasing:
                    slopes.reverse()
                lines = [(slope, rng.randrange(-10**6, 10**6)) for slope in slopes]
                container = MonotoneConvexHullTrick(minimize, increasing)
                for line in lines:
                    container.add_line(*line)
                for _ in range(200):
                    point = rng.randrange(-10**6, 10**6)
                    values = [slope * point + intercept for slope, intercept in lines]
                    expected = min(values) if minimize else max(values)
                    assert container.query(point) == expected
