import random

import pytest

from library_codex.algorithm.Search import kth_element


@pytest.mark.parametrize("size", [1, 2, 3, 64, 65, 1000])
def test_kth_element_matches_sorted(size):
    rng = random.Random(9000 + size)
    cases = [
        [rng.randrange(10**9) for _ in range(size)],
        list(range(size)),
        list(range(size - 1, -1, -1)),
        [rng.randrange(8) for _ in range(size)],
    ]
    for values in cases:
        before = values[:]
        expected = sorted(values)
        for index in {0, size // 2, size - 1}:
            assert kth_element(values, index) == expected[index]
        assert values == before


def test_kth_element_rejects_out_of_range_index():
    with pytest.raises(IndexError):
        kth_element([], 0)
    with pytest.raises(IndexError):
        kth_element([1], -1)
    with pytest.raises(IndexError):
        kth_element([1], 1)
