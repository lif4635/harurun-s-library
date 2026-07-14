import random

from library_codex.algorithm.SequenceOrdering import PointUpdateLexSort


def test_point_update_lex_sort_against_materialized_versions():
    rng = random.Random(716)
    for length in range(1, 80):
        current = [rng.randrange(10) for _ in range(length)]
        versions = [current[:]]
        sorter = PointUpdateLexSort(current)
        handles = [sorter.last()]
        for _ in range(200):
            position = rng.randrange(length)
            value = rng.randrange(10)
            current = current[:]
            current[position] = value
            versions.append(current)
            handles.append(sorter.mutate(position, value))
        ranks = sorter.proc()
        ordered = {tuple(value): rank for rank, value in enumerate(
            sorted({tuple(value) for value in versions})
        )}
        expected = [ordered[tuple(value)] for value in versions]
        assert ranks == expected
        assert [int(handle) for handle in handles] == expected
        assert sorter.maxSortedPos() == len(ordered) - 1

