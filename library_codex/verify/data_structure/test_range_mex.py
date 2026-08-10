import random

from library_codex.range_query.RangeMex import range_mex


def _mex(values):
    present = set(values)
    result = 0
    while result in present:
        result += 1
    return result


def test_range_mex_against_brute():
    rng = random.Random(671239)
    for length in range(50):
        for _ in range(30):
            values = [rng.randrange(-5, length + 6) for _ in range(length)]
            queries = [
                (rng.randrange(length + 1), rng.randrange(length + 1))
                for _ in range(100)
            ]
            queries = [
                (min(left, right), max(left, right))
                for left, right in queries
            ]
            expected = [_mex(values[left:right]) for left, right in queries]
            assert range_mex(values, queries) == expected


def test_range_mex_boundaries_and_validation():
    assert range_mex([], [(0, 0)]) == [0]
    assert range_mex([0, 1, 2], [(0, 3), (1, 1), (1, 3)]) == [3, 0, 0]
    for invalid in ((-1, 0), (0, 4), (2, 1)):
        try:
            range_mex([1, 2, 3], [invalid])
        except ValueError:
            pass
        else:
            raise AssertionError("invalid interval must be rejected")
