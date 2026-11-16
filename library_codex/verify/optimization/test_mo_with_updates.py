import random

import pytest

from library_codex.optimization.MoWithUpdates import MoWithUpdates


@pytest.mark.parametrize("width", [None, 1, 4, 100])
def test_random_updates_and_repeated_runs(width):
    rng = random.Random(7419)
    for n in range(25):
        values = [rng.randrange(9) for _ in range(n)]
        mo = MoWithUpdates(values, width)
        current = values.copy()
        expected = []
        for _ in range(100):
            if n and rng.randrange(2):
                i, value = rng.randrange(n), rng.randrange(9)
                mo.set(i, value)
                current[i] = value
            else:
                left = rng.randrange(n + 1)
                right = rng.randrange(left, n + 1)
                assert mo.query(left, right) == len(expected)
                expected.append(tuple(sorted(current[left:right])))
        counts = [0] * 9

        def add(value):
            counts[value] += 1

        def remove(value):
            counts[value] -= 1
            assert counts[value] >= 0

        def get():
            return tuple(value for value, count in enumerate(counts) for _ in range(count))

        assert mo.run(add, remove, get) == expected
        assert counts == [0] * 9
        assert mo.run(add, remove, get) == expected
        assert mo.values == values


def test_no_updates_and_validation():
    mo = MoWithUpdates([1, 2, 3])
    mo.query(0, 3)
    mo.query(1, 1)
    active = []
    assert mo.run(active.append, active.remove, lambda: sum(active)) == [6, 0]
    assert not active
    with pytest.raises(IndexError):
        mo.set(-1, 0)
    with pytest.raises(IndexError):
        mo.query(2, 1)
    with pytest.raises(ValueError):
        MoWithUpdates([], 0)
    assert MoWithUpdates([]).run(None, None, None) == []
