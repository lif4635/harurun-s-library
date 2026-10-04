import importlib
import random

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


def test_only_live_values_keep_trees():
    solver = PointSetRangeFrequency([0, 0])
    for value in range(1, 1000):
        solver.set(0, value)
        assert set(solver.positions) == {0, value}
    solver.set(1, 999)
    assert set(solver.positions) == {999}


def test_existing_values_do_not_allocate_trees(monkeypatch):
    module = importlib.import_module("library_codex.ordered_set.PointSetRangeFrequency")
    original = module.TreapSet
    created = []

    def make_tree():
        created.append(1)
        return original()

    monkeypatch.setattr(module, "TreapSet", make_tree)
    solver = PointSetRangeFrequency([1] * 100 + [2] * 100)
    assert len(created) == 2
    solver.set(0, 1)
    solver.set(0, 2)
    assert len(created) == 2
    solver.set(0, 3)
    assert len(created) == 3


def test_debug_output_does_not_change_queries():
    solver = PointSetRangeFrequency([3, 1, 3])
    solver.set(1, 2)
    assert str(solver) == "[3, 2, 3]"
    assert repr(solver) == "PointSetRangeFrequency([3, 2, 3])"
    values = solver.tolist()
    values[0] = 9
    assert solver.tolist() == [3, 2, 3]
    assert solver.query(0, 3, 3) == 2
