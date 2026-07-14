import itertools
import random

from library_codex.convolution.IncreasingSequences import (
    number_of_increasing_sequences_between,
)


def test_increasing_sequences_against_brute_force():
    rng = random.Random(449)
    for size in range(1, 9):
        for _ in range(100):
            lower = [rng.randrange(-3, 5) for _ in range(size)]
            upper = [rng.randrange(-2, 7) for _ in range(size)]
            minimum = min(lower)
            maximum = max(upper)
            expected = 0
            for values in itertools.combinations_with_replacement(
                range(minimum, maximum), size
            ):
                if all(lower[i] <= values[i] < upper[i] for i in range(size)):
                    expected += 1
            assert number_of_increasing_sequences_between(
                lower, upper
            ) == expected
