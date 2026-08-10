from random import Random

from library_codex.range_query.RangeXorBasis import (
    range_max_xor,
    range_xor_basis,
)


def _span(values):
    result = {0}
    for value in values:
        result |= {current ^ value for current in tuple(result)}
    return result


def test_range_xor_basis_matches_all_subset_xors():
    rng = Random(4441)
    for n in range(13):
        for _ in range(80):
            values = [rng.randrange(32) for _ in range(n)]
            queries = []
            for _ in range(20):
                left = rng.randrange(n + 1)
                right = rng.randrange(left, n + 1)
                queries.append((left, right))
            bases = range_xor_basis(values, queries)
            maximum = range_max_xor(values, queries, 7)
            for query_id, (left, right) in enumerate(queries):
                expected = _span(values[left:right])
                assert _span(bases[query_id]) == expected
                assert maximum[query_id] == max(value ^ 7 for value in expected)


def test_range_xor_basis_rejects_negative_values():
    try:
        range_xor_basis([1, -1], [(0, 2)])
    except ValueError:
        pass
    else:
        raise AssertionError("negative values must be rejected")
