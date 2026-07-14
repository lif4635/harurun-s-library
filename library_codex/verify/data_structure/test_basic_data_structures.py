from collections import deque
import bisect
import heapq
import random

from library_codex.data_structure.BinaryTrie import BinaryTrie
from library_codex.data_structure.FastSet import FastSet
from library_codex.data_structure.DynamicSegmentTree import (
    DynamicLazySegmentTree,
    DynamicSegmentTree,
    PersistentLazySegmentTree,
)
from library_codex.data_structure.FenwickTree import (
    DynamicFenwickTree,
    FenwickTree,
    FenwickTree2D,
    RangeAddRangeSum,
)
from library_codex.data_structure.SWAG import (
    ErasableHeap,
    SWAGDeque,
    SWAGQueue,
)
from library_codex.data_structure.SegmentTree import (
    DualSegmentTree,
    LazySegmentTree,
    SegmentTree,
)
from library_codex.data_structure.UnionFind import (
    DynamicUnionFind,
    EnumerateUnionFind,
    MonoidUnionFind,
    PartialPersistentUnionFind,
    RangeParallelUnionFind,
    UnionFind,
    WeightedUnionFind,
)


def test_fenwick_variants_random():
    rng = random.Random(820413)
    for size in range(1, 100):
        values = [rng.randrange(20) for _ in range(size)]
        fenwick = FenwickTree(values)
        dynamic = DynamicFenwickTree(size)
        for index, value in enumerate(values):
            dynamic.add(index, value)
        for _ in range(500):
            if rng.randrange(3) == 0:
                index = rng.randrange(size)
                delta = rng.randrange(-10, 11)
                values[index] += delta
                fenwick.add(index, delta)
                dynamic.add(index, delta)
            else:
                left = rng.randrange(size + 1)
                right = rng.randrange(left, size + 1)
                expected = sum(values[left:right])
                assert fenwick.sum(left, right) == expected
                assert dynamic.sum(left, right) == expected

        positive = [rng.randrange(1, 20) for _ in range(size)]
        fenwick = FenwickTree(positive)
        prefix = [0]
        for value in positive:
            prefix.append(prefix[-1] + value)
        for target in range(prefix[-1] + 2):
            expected = (
                max(0, bisect.bisect_left(prefix, target) - 1)
                if target > 0
                else 0
            )
            assert fenwick.lower_bound(target) == expected

    values = [0] * 80
    solver = RangeAddRangeSum(values)
    for _ in range(5000):
        left = rng.randrange(81)
        right = rng.randrange(left, 81)
        if rng.randrange(2):
            delta = rng.randrange(-50, 51)
            solver.add(left, right, delta)
            for index in range(left, right):
                values[index] += delta
        else:
            assert solver.sum(left, right) == sum(values[left:right])


def test_fenwick_2d_random():
    rng = random.Random(136802)
    height = 20
    width = 25
    values = [[0] * width for _ in range(height)]
    solver = FenwickTree2D(height, width)
    for _ in range(5000):
        if rng.randrange(2):
            row = rng.randrange(height)
            column = rng.randrange(width)
            delta = rng.randrange(-20, 21)
            values[row][column] += delta
            solver.add(row, column, delta)
        else:
            top = rng.randrange(height + 1)
            bottom = rng.randrange(top, height + 1)
            left = rng.randrange(width + 1)
            right = rng.randrange(left, width + 1)
            expected = sum(
                sum(row[left:right]) for row in values[top:bottom]
            )
            assert solver.sum(top, left, bottom, right) == expected


def test_segment_tree_noncommutative_and_search():
    rng = random.Random(791520)
    values = [chr(97 + rng.randrange(26)) for _ in range(100)]
    solver = SegmentTree(values, lambda first, second: first + second, "")
    for _ in range(5000):
        if rng.randrange(3) == 0:
            index = rng.randrange(len(values))
            value = chr(97 + rng.randrange(26))
            values[index] = value
            solver.set(index, value)
        else:
            left = rng.randrange(len(values) + 1)
            right = rng.randrange(left, len(values) + 1)
            assert solver.prod(left, right) == "".join(values[left:right])

    numbers = [rng.randrange(1, 10) for _ in range(100)]
    solver = SegmentTree(numbers, lambda x, y: x + y, 0)
    for left in range(101):
        limit = rng.randrange(100)
        right = left
        total = 0
        while right < 100 and total + numbers[right] <= limit:
            total += numbers[right]
            right += 1
        assert solver.max_right(left, lambda value: value <= limit) == right
    for right in range(101):
        limit = rng.randrange(100)
        left = right
        total = 0
        while left and total + numbers[left - 1] <= limit:
            left -= 1
            total += numbers[left]
        assert solver.min_left(right, lambda value: value <= limit) == left


def test_lazy_and_dual_segment_tree_random():
    rng = random.Random(490213)
    size = 100
    values = [rng.randrange(-50, 51) for _ in range(size)]
    solver = LazySegmentTree(
        values,
        lambda first, second: first + second,
        0,
        lambda action, value, length: value + action * length,
        lambda new, old: new + old,
    )
    dual = DualSegmentTree(
        values,
        lambda action, value: value + action,
        lambda new, old: new + old,
    )
    for _ in range(10000):
        kind = rng.randrange(5)
        if kind <= 1:
            left = rng.randrange(size + 1)
            right = rng.randrange(left, size + 1)
            delta = rng.randrange(-30, 31)
            solver.apply(left, right, delta)
            dual.apply(left, right, delta)
            for index in range(left, right):
                values[index] += delta
        elif kind == 2:
            index = rng.randrange(size)
            value = rng.randrange(-50, 51)
            values[index] = value
            solver.set(index, value)
            dual.set(index, value)
        elif kind == 3:
            left = rng.randrange(size + 1)
            right = rng.randrange(left, size + 1)
            assert solver.prod(left, right) == sum(values[left:right])
        else:
            index = rng.randrange(size)
            assert solver.get(index) == dual.get(index) == values[index]
    assert solver.all_prod() == sum(values)


def naive_groups(size, edges):
    graph = [[] for _ in range(size)]
    for first, second in edges:
        graph[first].append(second)
        graph[second].append(first)
    group = [-1] * size
    result = []
    for start in range(size):
        if group[start] >= 0:
            continue
        group[start] = len(result)
        row = []
        stack = [start]
        while stack:
            node = stack.pop()
            row.append(node)
            for other in graph[node]:
                if group[other] < 0:
                    group[other] = group[start]
                    stack.append(other)
        result.append(row)
    return group, result


def test_union_find_variants_random():
    rng = random.Random(624018)
    size = 100
    solver = UnionFind(size)
    enumerate_solver = EnumerateUnionFind(size)
    dynamic = DynamicUnionFind()
    edges = []
    for _ in range(3000):
        first = rng.randrange(size)
        second = rng.randrange(size)
        edges.append((first, second))
        solver.merge(first, second)
        enumerate_solver.merge(first, second)
        dynamic.merge(str(first), str(second))
        group, groups = naive_groups(size, edges)
        for _ in range(3):
            node = rng.randrange(size)
            other = rng.randrange(size)
            expected = group[node] == group[other]
            assert solver.same(node, other) == expected
            assert dynamic.same(str(node), str(other)) == expected
            assert solver.size(node) == len(groups[group[node]])
            assert sorted(enumerate_solver.members(node)) == sorted(
                groups[group[node]]
            )


def test_weighted_union_find_random_consistent_constraints():
    rng = random.Random(502137)
    size = 200
    values = [rng.randrange(-1000, 1001) for _ in range(size)]
    solver = WeightedUnionFind(size)
    for _ in range(5000):
        first = rng.randrange(size)
        second = rng.randrange(size)
        difference = values[second] - values[first]
        assert solver.merge(first, second, difference)
        assert solver.diff(first, second) == difference
    for first in range(size):
        for second in range(size):
            if solver.same(first, second):
                assert solver.diff(first, second) == values[second] - values[first]


def test_swag_queue_and_deque_noncommutative():
    rng = random.Random(973102)
    queue = SWAGQueue(lambda first, second: first + second, "")
    expected = deque()
    for _ in range(10000):
        if expected and rng.randrange(3) == 0:
            assert queue.popleft() == expected.popleft()
        else:
            value = chr(97 + rng.randrange(26))
            queue.append(value)
            expected.append(value)
        assert queue.fold() == "".join(expected)

    solver = SWAGDeque(lambda first, second: first + second, "")
    expected = deque()
    for _ in range(20000):
        kind = rng.randrange(4) if expected else rng.randrange(2)
        value = chr(97 + rng.randrange(26))
        if kind == 0:
            solver.appendleft(value)
            expected.appendleft(value)
        elif kind == 1:
            solver.append(value)
            expected.append(value)
        elif kind == 2:
            assert solver.popleft() == expected.popleft()
        else:
            assert solver.pop() == expected.pop()
        assert solver.fold() == "".join(expected)


def test_erasable_heap_random():
    rng = random.Random(350917)
    solver = ErasableHeap()
    values = []
    for _ in range(10000):
        if values and rng.randrange(3) == 0:
            value = rng.choice(values)
            values.remove(value)
            solver.erase(value)
        else:
            value = rng.randrange(100)
            values.append(value)
            solver.push(value)
        assert len(solver) == len(values)
        if values:
            assert solver.top() == min(values)


def test_binary_trie_random_multiset_and_lazy_xor():
    rng = random.Random(820641)
    bit_length = 10
    mask = (1 << bit_length) - 1
    solver = BinaryTrie(bit_length)
    values = []
    for _ in range(20000):
        kind = rng.randrange(7)
        if kind <= 1:
            value = rng.randrange(mask + 1)
            solver.add(value)
            bisect.insort(values, value)
        elif kind == 2 and values:
            value = rng.choice(values)
            solver.discard(value)
            values.remove(value)
        elif kind == 3:
            value = rng.randrange(mask + 1)
            solver.xor_all(value)
            values = sorted(item ^ value for item in values)
        elif values:
            index = rng.randrange(len(values))
            value = rng.randrange(mask + 1)
            assert solver.kth(index) == values[index]
            assert solver.bisect_left(value) == bisect.bisect_left(values, value)
            assert solver.xor_min(value) == min(values, key=lambda item: item ^ value)
            assert solver.xor_max(value) == max(values, key=lambda item: item ^ value)
        assert len(solver) == len(values)


def test_fast_set_random_next_prev():
    rng = random.Random(624913)
    for size in [1, 2, 63, 64, 65, 100, 1000, 10000]:
        solver = FastSet(size)
        values = []
        present = set()
        for _ in range(10000):
            value = rng.randrange(size)
            if rng.randrange(2):
                expected = value not in present
                assert solver.add(value) == expected
                if expected:
                    present.add(value)
                    bisect.insort(values, value)
            else:
                expected = value in present
                assert solver.discard(value) == expected
                if expected:
                    present.remove(value)
                    values.remove(value)
            query = rng.randrange(-2, size + 2)
            index = bisect.bisect_left(values, query)
            expected_next = values[index] if index < len(values) else -1
            index = bisect.bisect_right(values, query) - 1
            expected_prev = values[index] if index >= 0 else -1
            assert solver.next(query) == expected_next
            assert solver.prev(query) == expected_prev
            assert len(solver) == len(values)


def test_dynamic_segment_tree_sparse_large_domain():
    rng = random.Random(752091)
    bound = 10**12
    solver = DynamicSegmentTree(
        -bound, bound, lambda first, second: first + second, 0
    )
    values = {}
    for _ in range(20000):
        if rng.randrange(2):
            index = rng.randrange(-bound, bound)
            value = rng.randrange(-100, 101)
            values[index] = value
            solver.set(index, value)
        else:
            left = rng.randrange(-bound, bound)
            right = rng.randrange(left, bound + 1)
            expected = sum(
                value for index, value in values.items() if left <= index < right
            )
            assert solver.prod(left, right) == expected
    assert solver.all_prod() == sum(values.values())


def test_dynamic_lazy_segment_tree_random_range_add_sum():
    rng = random.Random(649125)
    size = 1000
    values = [0] * size
    solver = DynamicLazySegmentTree(
        0,
        size,
        lambda first, second: first + second,
        0,
        lambda action, aggregate, length: aggregate + action * length,
        lambda new, old: new + old,
    )
    for _ in range(10000):
        left = rng.randrange(size + 1)
        right = rng.randrange(left, size + 1)
        if rng.randrange(2):
            delta = rng.randrange(-30, 31)
            solver.apply(left, right, delta)
            for index in range(left, right):
                values[index] += delta
        else:
            assert solver.prod(left, right) == sum(values[left:right])
    assert solver.all_prod() == sum(values)


def test_persistent_lazy_segment_tree_branched_versions():
    rng = random.Random(136957)
    size = 80
    solver = PersistentLazySegmentTree(
        0,
        size,
        lambda first, second: first + second,
        0,
        lambda action, aggregate, length: aggregate + action * length,
        lambda new, old: new + old,
    )
    versions = [[0] * size]
    for _ in range(5000):
        base = rng.randrange(len(versions))
        left = rng.randrange(size + 1)
        right = rng.randrange(left, size + 1)
        delta = rng.randrange(-20, 21)
        version = solver.apply(left, right, delta, base)
        values = versions[base].copy()
        for index in range(left, right):
            values[index] += delta
        versions.append(values)
        assert version == len(versions) - 1
        for _ in range(3):
            query_version = rng.randrange(len(versions))
            query_left = rng.randrange(size + 1)
            query_right = rng.randrange(query_left, size + 1)
            assert solver.prod(
                query_left, query_right, query_version
            ) == sum(versions[query_version][query_left:query_right])


def test_monoid_and_partial_persistent_union_find():
    rng = random.Random(920174)
    size = 100
    values = [rng.randrange(-20, 21) for _ in range(size)]
    monoid = MonoidUnionFind(values, lambda first, second: first + second)
    persistent = PartialPersistentUnionFind(size)
    edges = []
    snapshots = []
    for time in range(300):
        first = rng.randrange(size)
        second = rng.randrange(size)
        edges.append((first, second))
        monoid.merge(first, second)
        persistent.merge(first, second, time)
        group, groups = naive_groups(size, edges)
        snapshots.append((group, groups))
        for _ in range(5):
            node = rng.randrange(size)
            assert monoid.get(node) == sum(values[vertex] for vertex in groups[group[node]])
            old_time = rng.randrange(time + 1)
            old_group, old_groups = snapshots[old_time]
            assert persistent.size(node, old_time) == len(old_groups[old_group[node]])
    for first in range(size):
        for second in range(size):
            expected = next(
                (
                    time
                    for time, (group, _) in enumerate(snapshots)
                    if group[first] == group[second]
                ),
                -1,
            )
            assert persistent.when_unite(first, second) == expected


def test_range_parallel_union_find_random():
    rng = random.Random(815024)
    size = 200
    solver = RangeParallelUnionFind(size)
    naive = UnionFind(size)
    for _ in range(3000):
        length = rng.randrange(size + 1)
        first = rng.randrange(size - length + 1)
        second = rng.randrange(size - length + 1)
        solver.merge(first, second, length)
        for offset in range(length):
            naive.merge(first + offset, second + offset)
        for _ in range(10):
            left = rng.randrange(size)
            right = rng.randrange(size)
            assert solver.same(left, right) == naive.same(left, right)
            assert solver.size(left) == naive.size(left)
