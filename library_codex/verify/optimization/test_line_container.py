import random

from library_codex.optimization.LineContainer import LineContainer


def test_line_container_all_objectives():
    rng = random.Random(187349)
    for minimize in (False, True):
        for _ in range(500):
            lines = [
                (rng.randrange(-10**9, 10**9), rng.randrange(-10**18, 10**18))
                for _ in range(200)
            ]
            container = LineContainer(minimize)
            for line in lines:
                container.add_line(*line)
            for _ in range(200):
                point = rng.randrange(-(1 << 62), 1 << 62)
                values = [slope * point + intercept for slope, intercept in lines]
                assert container.query(point) == (
                    min(values) if minimize else max(values)
                )
