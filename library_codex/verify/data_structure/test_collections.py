from collections import deque
import bisect
import random

from library_codex.data_structure.Collections import (
    BitSet,
    PersistentBinaryTrie,
    PersistentQueue,
    PointSetRangeFrequency,
    RangeSet,
    TopKSum,
    TreapSet,
    sliding_window_minimum,
)


def test_bitset_random_against_integer():
    rng = random.Random(810529)
    size = 500
    solver = BitSet(size)
    value = 0
    mask = (1 << size) - 1
    for _ in range(20000):
        kind = rng.randrange(4)
        index = rng.randrange(size)
        if kind == 0:
            solver.set(index)
            value |= 1 << index
        elif kind == 1:
            solver.reset(index)
            value &= ~(1 << index)
        elif kind == 2:
            solver.flip(index)
            value ^= 1 << index
        else:
            solver.flip()
            value ^= mask
        assert int(solver) == value
        assert solver.count() == value.bit_count()
        query = rng.randrange(-2, size + 2)
        shifted = value >> max(0, query)
        expected_next = (
            max(0, query) + (shifted & -shifted).bit_length() - 1
            if shifted
            else -1
        )
        clipped = min(query, size - 1)
        expected_prev = (
            (value & ((1 << (clipped + 1)) - 1)).bit_length() - 1
            if clipped >= 0
            else -1
        )
        assert solver.find_next(query) == expected_next
        assert solver.find_prev(query) == expected_prev


def test_treap_set_random_order_statistics():
    rng = random.Random(391720)
    solver = TreapSet()
    values = []
    for _ in range(50000):
        value = rng.randrange(-1000, 1001)
        if rng.randrange(2):
            index = bisect.bisect_left(values, value)
            expected = index == len(values) or values[index] != value
            assert solver.add(value) == expected
            if expected:
                values.insert(index, value)
        else:
            index = bisect.bisect_left(values, value)
            expected = index < len(values) and values[index] == value
            assert solver.discard(value) == expected
            if expected:
                values.pop(index)
        query = rng.randrange(-1100, 1101)
        assert solver.bisect_left(query) == bisect.bisect_left(values, query)
        assert solver.bisect_right(query) == bisect.bisect_right(values, query)
        if values:
            index = rng.randrange(len(values))
            assert solver.kth(index) == values[index]
        assert list(solver) == values


def test_point_set_range_frequency_random():
    rng = random.Random(592016)
    size = 200
    values = [rng.randrange(20) for _ in range(size)]
    solver = PointSetRangeFrequency(values)
    for _ in range(20000):
        if rng.randrange(2):
            index = rng.randrange(size)
            value = rng.randrange(20)
            values[index] = value
            solver.set(index, value)
        else:
            left = rng.randrange(size + 1)
            right = rng.randrange(left, size + 1)
            value = rng.randrange(20)
            assert solver.query(left, right, value) == values[left:right].count(value)


def test_range_set_random_boolean_universe():
    rng = random.Random(731028)
    size = 300
    present = [False] * size
    solver = RangeSet()
    for _ in range(20000):
        left = rng.randrange(size + 1)
        right = rng.randrange(left, size + 1)
        if rng.randrange(2):
            solver.add(left, right)
            present[left:right] = [True] * (right - left)
        else:
            solver.discard(left, right)
            present[left:right] = [False] * (right - left)
        assert solver.covered_length == sum(present)
        value = rng.randrange(size)
        assert solver.contains(value) == present[value]
        expected = value
        while expected < size and present[expected]:
            expected += 1
        assert solver.mex(value) == expected
        reconstructed = [False] * size
        for interval_left, interval_right in solver.intervals():
            reconstructed[interval_left:interval_right] = [True] * (
                interval_right - interval_left
            )
        assert reconstructed == present


def test_persistent_queue_branched_versions():
    rng = random.Random(240719)
    solver = PersistentQueue()
    versions = [deque()]
    for _ in range(20000):
        base = rng.randrange(len(versions))
        current = versions[base].copy()
        if current and rng.randrange(3) == 0:
            version = solver.popleft(base)
            current.popleft()
        else:
            value = rng.randrange(1000)
            version = solver.append(value, base)
            current.append(value)
        versions.append(current)
        assert version == len(versions) - 1
        for _ in range(3):
            index = rng.randrange(len(versions))
            if versions[index]:
                assert solver.front(index) == versions[index][0]


def test_persistent_binary_trie_branched_versions():
    rng = random.Random(520183)
    bit_length = 10
    solver = PersistentBinaryTrie(bit_length)
    versions = [[]]
    for _ in range(10000):
        base = rng.randrange(len(versions))
        values = versions[base].copy()
        if values and rng.randrange(3) == 0:
            value = rng.choice(values)
            version = solver.discard(value, base)
            values.remove(value)
        else:
            value = rng.randrange(1 << bit_length)
            version = solver.add(value, base)
            values.append(value)
        values.sort()
        versions.append(values)
        assert version == len(versions) - 1
        for _ in range(3):
            index = rng.randrange(len(versions))
            if versions[index]:
                kth = rng.randrange(len(versions[index]))
                assert solver.kth(kth, index) == versions[index][kth]
                xor = rng.randrange(1 << bit_length)
                assert solver.xor_min(xor, index) == min(
                    value ^ xor for value in versions[index]
                )


def test_top_k_sum_random_multiset():
    rng = random.Random(671904)
    for largest in (False, True):
        for k in range(10):
            solver = TopKSum(k, largest)
            values = []
            for _ in range(10000):
                if values and rng.randrange(3) == 0:
                    value = rng.choice(values)
                    values.remove(value)
                    solver.discard(value)
                else:
                    value = rng.randrange(-30, 31)
                    values.append(value)
                    solver.add(value)
                ordered = sorted(values, reverse=largest)
                assert solver.sum() == sum(ordered[:k])


def test_sliding_window_minimum_random():
    rng = random.Random(420817)
    for size in range(1, 200):
        values = [rng.randrange(-100, 101) for _ in range(size)]
        for width in range(1, size + 1):
            expected = [
                min(values[index:index + width])
                for index in range(size - width + 1)
            ]
            assert sliding_window_minimum(values, width) == expected
