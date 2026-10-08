import random
from collections import deque

import pytest

from library_codex.sequence_structure.Deque import Deque


def test_deque_against_standard_queue():
    rng = random.Random(20261009)
    queue = Deque()
    expected = deque()
    for step in range(20000):
        kind = rng.randrange(6) if expected else rng.randrange(2)
        value = rng.randrange(-100, 101)
        if kind == 0:
            queue.appendleft(value)
            expected.appendleft(value)
        elif kind == 1:
            queue.append(value)
            expected.append(value)
        elif kind == 2:
            assert queue.popleft() == expected.popleft()
        elif kind == 3:
            assert queue.pop() == expected.pop()
        else:
            index = rng.randrange(-len(expected), len(expected))
            if kind == 4:
                queue[index] = value
                expected[index] = value
            assert queue[index] == expected[index]
        assert len(queue) == len(expected)
        if step % 31 == 0:
            assert queue.tolist() == list(expected)
            assert list(queue) == list(expected)
            assert str(queue) == str(list(expected))
            assert repr(queue) == 'Deque(' + str(list(expected)) + ')'


def test_deque_rebalancing_and_empty_errors():
    for n in (0, 1, 2, 3, 7, 8, 9, 1024, 1025):
        queue = Deque(iter(range(n)))
        assert [queue.popleft() for _ in range(n)] == list(range(n))
        for i in range(n):
            queue.appendleft(i)
        assert [queue.pop() for _ in range(n)] == list(range(n))
        for method in (queue.pop, queue.popleft):
            with pytest.raises(IndexError):
                method()
        for index in (-1, 0, 1):
            with pytest.raises(IndexError):
                queue[index]
            with pytest.raises(IndexError):
                queue[index] = 0
    queue = Deque([None, {'a': 1}])
    copied = queue.tolist()
    copied.clear()
    assert queue[0] is None
    assert queue[-1] == {'a': 1}
    with pytest.raises(IndexError):
        queue[-3]
    with pytest.raises(IndexError):
        queue[2] = 0


def test_deque_long_mixed_ends():
    queue = Deque(range(20000))
    for i in range(30000):
        assert queue.popleft() == i
        queue.append(i + 20000)
        queue.appendleft(None)
        assert queue.popleft() is None
    assert queue.tolist() == list(range(30000, 50000))
