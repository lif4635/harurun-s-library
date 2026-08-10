import random

from library_codex.algorithm.ParallelBinarySearch import parallel_binary_search


def test_parallel_binary_search_both_monotone_directions():
    rng = random.Random(319827)
    for update_count in range(1, 80):
        increments = [rng.randrange(1, 20) for _ in range(update_count)]
        prefix = [0]
        for value in increments:
            prefix.append(prefix[-1] + value)
        thresholds = [rng.randrange(1, prefix[-1] + 1) for _ in range(100)]
        state = [0]

        def reset():
            state[0] = 0

        def update(index):
            state[0] += increments[index]

        first_true = parallel_binary_search(
            len(thresholds),
            update_count,
            0,
            reset,
            update,
            lambda query: state[0] >= thresholds[query],
        )
        expected_first = [
            next(index for index, total in enumerate(prefix) if total >= threshold)
            for threshold in thresholds
        ]
        assert first_true == expected_first

        limits = [rng.randrange(prefix[-1]) for _ in range(100)]
        last_true = parallel_binary_search(
            len(limits),
            0,
            update_count,
            reset,
            update,
            lambda query: state[0] <= limits[query],
        )
        expected_last = [
            max(index for index, total in enumerate(prefix) if total <= limit)
            for limit in limits
        ]
        assert last_true == expected_last


def test_parallel_binary_search_empty_queries():
    assert parallel_binary_search(0, 10, 0, lambda: None, lambda _: None, lambda _: True) == []
