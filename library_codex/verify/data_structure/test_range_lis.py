import random

from library_codex.data_structure.RangeLIS import RangeLIS, lis_brute


def test_range_lis_against_patience_sorting():
    rng = random.Random(765)
    for size in range(1, 130):
        values = [rng.randrange(30) for _ in range(size)]
        structure = RangeLIS(values)
        for _ in range(1000):
            left = rng.randrange(size + 1)
            right = rng.randrange(left, size + 1)
            assert structure.query(left, right) == lis_brute(values[left:right])

