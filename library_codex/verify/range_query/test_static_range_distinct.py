import random

from library_codex.range_query.StaticRangeDistinct import StaticRangeDistinct


def test_static_range_distinct_random():
    rng = random.Random(918273)
    for size in range(35):
        for _ in range(12):
            values = [rng.randrange(-5, 7) for _ in range(size)]
            query = StaticRangeDistinct(values)
            for _ in range(80):
                left = rng.randrange(size + 1)
                right = rng.randrange(left, size + 1)
                assert query.count(left, right) == len(set(values[left:right]))
