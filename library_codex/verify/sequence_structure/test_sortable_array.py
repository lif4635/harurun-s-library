import random

import pytest

from library_codex.sequence_structure.SortableArray import SortableArray


def test_random_noncommutative():
    rng = random.Random(81273)
    for n in range(1, 55):
        keys = rng.sample(range(-10000, 10000), n)
        expected = [(key, chr(65 + i % 26)) for i, key in enumerate(keys)]
        data = SortableArray(lambda a, b: a + b, "", expected)
        for step in range(150):
            left = rng.randrange(n + 1)
            right = rng.randrange(left, n + 1)
            kind = rng.randrange(4)
            if kind < 2:
                data.sort(left, right, kind == 1)
                expected[left:right] = sorted(expected[left:right], reverse=kind == 1)
            elif kind == 2:
                index = rng.randrange(n)
                item = (100000 + step, chr(97 + step % 26))
                data.set(index, *item)
                expected[index] = item
            else:
                assert data.prod(left, right) == "".join(v for k, v in expected[left:right])
            assert data.tolist() == expected
            assert data.all_prod() == "".join(v for k, v in expected)
            index = rng.randrange(n)
            assert data.get(index) == expected[index]
            assert len(data._keys) == n + 1


def test_empty_invalid_and_debug():
    data = SortableArray(lambda a, b: a + b, 0, [])
    assert len(data) == 0
    assert data.prod(0, 0) == data.all_prod() == 0
    data.sort(0, 0)
    assert data.tolist() == []
    with pytest.raises(IndexError):
        data.get(0)
    with pytest.raises(IndexError):
        data.prod(-1, 0)
    with pytest.raises(ValueError):
        SortableArray(lambda a, b: a + b, 0, [(1, 3), (1, 2)])
    data = SortableArray(lambda a, b: a + b, 0, [(2, 7), (1, 5)])
    with pytest.raises(ValueError):
        data.set(0, 1, 10)
    assert str(data) == str([(2, 7), (1, 5)])
    assert repr(data) == 'SortableArray([(2, 7), (1, 5)])'
    data.set(0, 2, 11)
    assert data.tolist() == [(2, 11), (1, 5)]
    assert data.prod(0, 2) == 16


def test_many_splits_and_merges():
    n = 10000
    data = SortableArray(lambda a, b: a + b, 0, [(n-i, i) for i in range(n)])
    for reverse in (False, True, False):
        data.sort(0, n, reverse)
        for i in range(0, n, 5):
            expected = 5 * (i + 2) if reverse else 5 * (n - 3 - i)
            assert data.prod(i, i + 5) == expected
        assert data.all_prod() == n * (n - 1) // 2
    assert data.tolist() == [(i + 1, n - i - 1) for i in range(n)]
