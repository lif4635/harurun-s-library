import heapq
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.data_structure.RadixHeap import RadixHeap


def test_random():
    radix = RadixHeap()
    heap = []
    items = Counter()
    uid = 0
    for _ in range(200000):
        assert bool(radix) == bool(heap)
        assert len(radix) == len(heap)
        if not heap or random.randrange(3):
            bits = random.randrange(0, 300)
            key = radix.last + random.getrandbits(bits)
            value = uid
            uid += 1
            radix.push(key, value)
            heapq.heappush(heap, key)
            items[key, value] += 1
            assert radix.top()[0] == heap[0]
        else:
            key, value = radix.pop()
            assert key == heapq.heappop(heap)
            assert items[key, value]
            items[key, value] -= 1

    while heap:
        key, value = radix.pop()
        assert key == heapq.heappop(heap)
        assert items[key, value]
        items[key, value] -= 1
    assert radix.empty()


def test_equal_and_huge_keys():
    radix = RadixHeap()
    for i in range(1000):
        radix.push(0, i)
    assert [radix.pop()[0] for _ in range(1000)] == [0] * 1000
    for i in range(1, 1001):
        radix.push((1 << (i * 10)) + i, i)
        key, value = radix.pop()
        assert key == (1 << (i * 10)) + i
        assert value == i


def test_monotone_constraint():
    radix = RadixHeap()
    radix.push(10, None)
    assert radix.pop()[0] == 10
    try:
        radix.push(9, None)
    except AssertionError:
        pass
    else:
        raise AssertionError("a key smaller than last was accepted")


def test_top_does_not_advance_last():
    radix = RadixHeap()
    radix.push(10, "ten")
    assert radix.top() == (10, "ten")
    assert radix.last == 0
    radix.push(5, "five")
    assert radix.pop() == (5, "five")
    assert radix.pop() == (10, "ten")


if __name__ == "__main__":
    random.seed(0)
    test_random()
    test_equal_and_huge_keys()
    test_monotone_constraint()
    test_top_does_not_advance_last()
