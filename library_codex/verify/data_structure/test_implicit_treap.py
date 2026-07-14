import random

from library_codex.data_structure.ImplicitTreap import ImplicitTreap


def test_implicit_treap_random_sequence_and_noncommutative_product():
    rng = random.Random(719203)
    values = [chr(97 + rng.randrange(26)) for _ in range(100)]
    solver = ImplicitTreap(values, lambda first, second: first + second, "")
    for _ in range(30000):
        kind = rng.randrange(7)
        if kind == 0:
            index = rng.randrange(len(values) + 1)
            value = chr(97 + rng.randrange(26))
            values.insert(index, value)
            solver.insert(index, value)
        elif kind == 1 and values:
            index = rng.randrange(len(values))
            assert solver.pop(index) == values.pop(index)
        elif kind == 2 and values:
            index = rng.randrange(len(values))
            value = chr(97 + rng.randrange(26))
            values[index] = value
            solver[index] = value
        elif kind == 3:
            left = rng.randrange(len(values) + 1)
            right = rng.randrange(left, len(values) + 1)
            values[left:right] = reversed(values[left:right])
            solver.reverse(left, right)
        elif kind == 4 and values:
            index = rng.randrange(len(values))
            assert solver[index] == values[index]
        else:
            left = rng.randrange(len(values) + 1)
            right = rng.randrange(left, len(values) + 1)
            assert solver.prod(left, right) == "".join(values[left:right])
        assert len(solver) == len(values)
        if rng.randrange(100) == 0:
            assert solver.to_list() == values
    assert solver.to_list() == values


def test_implicit_treap_lazy_range_add_sum_and_reverse():
    rng = random.Random(820516)
    values = [rng.randrange(-50, 51) for _ in range(200)]
    solver = ImplicitTreap(
        values,
        lambda first, second: first + second,
        0,
        lambda action, aggregate, length: aggregate + action * length,
        lambda new, old: new + old,
    )
    for _ in range(30000):
        left = rng.randrange(len(values) + 1)
        right = rng.randrange(left, len(values) + 1)
        kind = rng.randrange(4)
        if kind == 0:
            delta = rng.randrange(-30, 31)
            solver.apply(left, right, delta)
            for index in range(left, right):
                values[index] += delta
        elif kind == 1:
            solver.reverse(left, right)
            values[left:right] = reversed(values[left:right])
        elif kind == 2:
            assert solver.prod(left, right) == sum(values[left:right])
        elif values:
            index = rng.randrange(len(values))
            assert solver[index] == values[index]
    assert solver.to_list() == values


def test_implicit_treap_deep_build_without_recursion():
    size = 200000
    solver = ImplicitTreap(range(size))
    assert len(solver) == size
    assert solver.prod() == size * (size - 1) // 2
    solver.reverse(0, size)
    assert solver[0] == size - 1
    assert solver[-1] == 0
