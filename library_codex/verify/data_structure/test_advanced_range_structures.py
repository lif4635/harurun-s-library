import random

from library_codex.data_structure.AdvancedRangeStructures import (
    LazyKDTree,
    RangeAddCountTopK,
    SortableSegmentTree,
)


def test_range_add_count_top_k_against_brute_force():
    rng = random.Random(762)
    for size in range(1, 100):
        values = [0] * size
        tree = RangeAddCountTopK(size, 7, 0, 1, -(10 ** 30), 0)
        for _ in range(500):
            left = rng.randrange(size)
            right = rng.randrange(left + 1, size + 1)
            if rng.randrange(3):
                delta = rng.randrange(-100, 101)
                tree.range_add(left, right, delta)
                for index in range(left, right):
                    values[index] += delta
            else:
                frequency = {}
                for value in values[left:right]:
                    frequency[value] = frequency.get(value, 0) + 1
                expected = sorted(frequency.items(), reverse=True)[:7]
                actual = tree.range_top_k(left, right)
                assert [(node.x, node.f) for node in actual[:len(expected)]] == expected


def test_lazy_kd_tree_rectangle_add_sum_and_point_set():
    rng = random.Random(763)
    for size in range(1, 100):
        xs = [rng.randrange(-30, 31) for _ in range(size)]
        ys = [rng.randrange(-30, 31) for _ in range(size)]
        values = [rng.randrange(-100, 101) for _ in range(size)]
        tree = LazyKDTree(xs, ys, values)
        for _ in range(500):
            left, right = sorted((rng.randrange(-35, 36), rng.randrange(-35, 36)))
            down, up = sorted((rng.randrange(-35, 36), rng.randrange(-35, 36)))
            if rng.randrange(4) == 0:
                index = rng.randrange(size)
                value = rng.randrange(-1000, 1001)
                values[index] = value
                tree.set(index, value)
            elif rng.randrange(2):
                delta = rng.randrange(-100, 101)
                tree.update(left, right, down, up, delta)
                for index in range(size):
                    if left <= xs[index] < right and down <= ys[index] < up:
                        values[index] += delta
            else:
                expected = sum(values[index] for index in range(size)
                               if left <= xs[index] < right
                               and down <= ys[index] < up)
                assert tree.query(left, right, down, up) == expected


def test_sortable_segment_tree_against_lists():
    rng = random.Random(764)
    for size in range(1, 200):
        keys = list(range(size))
        rng.shuffle(keys)
        values = [chr(33 + index % 80) for index in range(size)]
        tree = SortableSegmentTree(
            keys, values, op=lambda first, second: first + second, identity=""
        )
        for _ in range(500):
            left = rng.randrange(size)
            right = rng.randrange(left + 1, size + 1)
            action = rng.randrange(3)
            if action == 0:
                pairs = sorted(zip(keys[left:right], values[left:right]),
                               reverse=bool(rng.randrange(2)))
                reverse = pairs == sorted(pairs, reverse=True)
                # Keys are distinct, so pair sorting and key sorting agree.
                tree.sort(left, right, reverse)
                keys[left:right] = [pair[0] for pair in pairs]
                values[left:right] = [pair[1] for pair in pairs]
            elif action == 1:
                index = rng.randrange(size)
                key = rng.randrange(10 ** 9)
                value = chr(rng.randrange(33, 113))
                keys[index] = key
                values[index] = value
                tree.update(index, key, value)
            else:
                assert tree.query(left, right) == "".join(values[left:right])

