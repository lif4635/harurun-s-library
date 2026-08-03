import random

from library_codex.data_structure.MaxInterval import max_interval_segment_tree


def brute_subarray_extrema(values):
    sums = [sum(values[left:right])
            for left in range(len(values))
            for right in range(left + 1, len(values) + 1)]
    return max(sums), min(sums)


def test_max_interval_segment_tree_random_point_updates():
    rng = random.Random(20260803)
    values = [rng.randrange(-30, 31) for _ in range(40)]
    tree = max_interval_segment_tree(values)
    for _ in range(1000):
        aggregate = tree.all_prod()
        expected_maximum, expected_minimum = brute_subarray_extrema(values)
        assert aggregate.sum == sum(values)
        assert aggregate.maximum == expected_maximum
        assert aggregate.minimum == expected_minimum

        index = rng.randrange(len(values))
        values[index] = rng.randrange(-30, 31)
        tree.set(index, type(aggregate).single(values[index]))
