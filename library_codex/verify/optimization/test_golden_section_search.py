import random

from library_codex.optimization.GoldenSectionSearch import golden_section_search


def test_integer_golden_section_search():
    rng = random.Random(981734)
    for _ in range(10000):
        center = rng.randrange(-10**9, 10**9)
        left = rng.randrange(-10**9, center + 1)
        right = rng.randrange(center, 10**9 + 1)
        point, value = golden_section_search(
            lambda x: (x - center) ** 2 + 7,
            left,
            right,
        )
        assert (point, value) == (center, 7)
