import random

import pytest

from library_codex.ordered_set.PointSetRangeFrequency import PointSetRangeFrequency


def test_random_updates_and_counts():
    rng = random.Random(592016)
    values = [rng.randrange(20) for _ in range(200)]
    solver = PointSetRangeFrequency(values)
    for _ in range(20000):
        if rng.randrange(2):
            index = rng.randrange(len(values))
            value = rng.randrange(20)
            values[index] = value
            solver.set(index, value)
        else:
            left = rng.randrange(len(values) + 1)
            right = rng.randrange(left, len(values) + 1)
            value = rng.randrange(20)
            assert solver.query(left, right, value) == values[left:right].count(value)


def test_initial_values_and_half_open_intervals():
    assert PointSetRangeFrequency([]).query(0, 0, 0) == 0
    assert PointSetRangeFrequency(4).query(0, 4, 0) == 4
    values = [(1, 2), (3, 4), (1, 2)]
    solver = PointSetRangeFrequency(values)
    assert solver.query(0, 2, (1, 2)) == 1
    assert solver.query(1, 3, (1, 2)) == 1
    assert solver.query(0, 3, (1, 2)) == 2
    assert solver.query(1, 1, (3, 4)) == 0
    solver.set(1, (1, 2))
    assert values[1] == (3, 4)
    assert solver.query(0, 3, (3, 4)) == 0


def test_only_live_values_keep_positions():
    solver = PointSetRangeFrequency([0, 0])
    for value in range(1, 1000):
        solver.set(0, value)
        assert set(solver.positions) == {0, value}
    solver.set(1, 999)
    assert set(solver.positions) == {999}


def test_split_merge_and_bounded_storage():
    rng = random.Random(27519)
    values = [0] * 4096
    solver = PointSetRangeFrequency(values)
    for step in range(12000):
        index = rng.randrange(len(values))
        value = rng.randrange(3)
        solver.set(index, value)
        values[index] = value
        left = rng.randrange(len(values) + 1)
        right = rng.randrange(left, len(values) + 1)
        assert solver.query(left, right, value) == values[left:right].count(value)
        if step % 100 == 0:
            stored = 0
            for key, (blocks, ends) in solver.positions.items():
                flat = [i for block in blocks for i in block]
                assert flat == [i for i, x in enumerate(values) if x == key]
                assert ends == [block[-1] for block in blocks]
                assert all(0 < len(block) <= 2 * solver.block_size for block in blocks)
                assert all(len(a) + len(b) > solver.block_size for a, b in zip(blocks, blocks[1:]))
                stored += len(flat)
            assert stored == len(values)


def test_negative_index_and_non_orderable_values():
    solver = PointSetRangeFrequency([None, "x", 1, (2,)])
    solver.set(-1, None)
    assert solver.query(0, 4, None) == 2
    assert solver.query(3, 2, None) == 0
    for index in (-5, 4):
        with pytest.raises(IndexError):
            solver.set(index, None)


def test_drain_and_refill_buckets():
    solver = PointSetRangeFrequency([0] * 1024)
    for direction in (range(1024), range(1023, -1, -1)):
        for index in direction:
            solver.set(index, 1)
            assert solver.query(index, index + 1, 1) == 1
        assert set(solver.positions) == {1}
        for index in direction:
            solver.set(index, 0)
            assert solver.query(index, index + 1, 0) == 1
        assert set(solver.positions) == {0}
        blocks, ends = solver.positions[0]
        assert ends == [block[-1] for block in blocks]
        assert sum(map(len, blocks)) == 1024
        assert len(blocks) <= 2 * 1024 // solver.block_size + 1


def test_debug_output_does_not_change_queries():
    solver = PointSetRangeFrequency([3, 1, 3])
    solver.set(1, 2)
    assert str(solver) == "[3, 2, 3]"
    assert repr(solver) == "PointSetRangeFrequency([3, 2, 3])"
    values = solver.tolist()
    values[0] = 9
    assert solver.tolist() == [3, 2, 3]
    assert solver.query(0, 3, 3) == 2
