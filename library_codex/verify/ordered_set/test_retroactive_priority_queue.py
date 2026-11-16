import heapq
import random
import pytest
from library_codex.ordered_set.RetroactivePriorityQueue import RetroactivePriorityQueue


def replay(operations, maximum):
    heap, popped = [], 0
    for t, (kind, value) in enumerate(operations):
        if kind == 1:
            heapq.heappush(heap, (-value if maximum else value, t, value))
        elif kind == 2 and heap:
            popped += heapq.heappop(heap)[2]
    return sorted((t, value) for _, t, value in heap), popped


@pytest.mark.parametrize("maximum", [False, True])
def test_retroactive_random_edits(maximum):
    rng = random.Random(88232)
    for n in (1, 2, 7, 32, 100):
        queue = RetroactivePriorityQueue(n, maximum)
        operations, current = [(0, 0)] * n, {}
        for _ in range(1200):
            t, kind, value = rng.randrange(n), rng.randrange(3), rng.randrange(-15, 16)
            if kind == 1:
                removed, added = queue.set_push(t, value)
            elif kind == 2:
                removed, added = queue.set_pop(t)
            else:
                removed, added = queue.erase(t)
            operations[t] = (kind, value)
            for time, old in removed:
                assert current.pop(time) == old
            for time, new in added:
                assert time not in current
                current[time] = new
            expected, popped = replay(operations, maximum)
            assert sorted(current.items()) == expected == queue.items()
            assert queue.sum() == sum(v for _, v in expected)
            assert queue.popped_sum() == popped
            assert len(queue) == len(expected)
            assert queue.peek() == ((max if maximum else min)(v for _, v in expected) if expected else None)
            assert all(queue.contains(i) == (i in current) for i in range(n))
            assert str(queue) == str(expected)
            assert repr(queue) == "RetroactivePriorityQueue(%r)" % expected


def test_empty_pops_ties_and_errors():
    queue = RetroactivePriorityQueue(5)
    for t in range(5):
        queue.set_pop(t)
    assert queue.items() == []
    queue.set_push(0, 4)
    queue.set_push(1, 4)
    assert queue.items() == []
    queue.erase(2)
    queue.erase(3)
    assert queue.items() == [(1, 4)]
    queue.erase(4)
    assert queue.items() == [(0, 4), (1, 4)]
    with pytest.raises(TypeError):
        queue.set_push(0, 1.5)
    assert queue.items() == [(0, 4), (1, 4)]
    with pytest.raises(IndexError):
        queue.erase(5)
    assert RetroactivePriorityQueue(0).peek() is None
