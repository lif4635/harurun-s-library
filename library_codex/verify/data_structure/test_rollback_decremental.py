import random

import pytest

from library_codex.ordered_set.DecrementalSet import DecrementalSet
from library_codex.sequence_structure.RollbackArray import RollbackArray


def test_rollback_array_snapshots_and_undo():
    array = RollbackArray([1, 2, 3])
    start = array.snapshot()
    array.set(1, 8)
    middle = array.snapshot()
    array.set(2, 9)
    assert array.tolist() == [1, 8, 9]
    array.rollback(middle)
    assert array.tolist() == [1, 8, 3]
    array.undo()
    assert array.tolist() == [1, 2, 3]
    assert array.snapshot() == start
    with pytest.raises(IndexError):
        array.undo()


def test_decremental_set_random_against_python_set():
    random.seed(20260823)
    for size in range(80):
        data = DecrementalSet(size)
        expected = set(range(size))
        for _ in range(400):
            value = random.randrange(-3, size + 3)
            if random.randrange(3) == 0:
                assert data.discard(value) == (value in expected)
                expected.discard(value)
            else:
                successors = [x for x in expected if x >= value]
                predecessors = [x for x in expected if x <= value]
                assert data.next(value) == (min(successors) if successors else -1)
                assert data.prev(value) == (max(predecessors) if predecessors else -1)
        assert data.tolist() == sorted(expected)
        assert len(data) == len(expected)
