import random
import pytest

from library_codex.sequence_structure.ImplicitTreap import ImplicitTreap


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


@pytest.mark.parametrize("commutative", [False, True])
def test_implicit_treap_lazy_range_add_sum_and_reverse(commutative):
    rng = random.Random(820516)
    values = [rng.randrange(-50, 51) for _ in range(200)]
    solver = ImplicitTreap(
        values,
        lambda first, second: first + second,
        0,
        lambda action, aggregate, length: aggregate + action * length,
        lambda new, old: new + old,
        commutative=commutative,
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


@pytest.mark.parametrize("commutative", [False, True])
def test_affine_updates_with_insert_pop_and_reverse(commutative):
    rng = random.Random(84341)
    mod = 998244353
    values = []
    solver = ImplicitTreap(
        values, lambda a, b: (a + b) % mod, 0,
        lambda f, x, n: (f[0] * x + f[1] * n) % mod,
        lambda f, g: (f[0] * g[0] % mod, (f[0] * g[1] + f[1]) % mod),
        commutative=commutative,
    )
    for _ in range(10000):
        kind = rng.randrange(6)
        left = rng.randrange(len(values) + 1)
        right = rng.randrange(left, len(values) + 1)
        if kind == 0 or not values:
            value = rng.randrange(mod)
            solver.insert(left, value)
            values.insert(left, value)
        elif kind == 1:
            index = rng.randrange(len(values))
            assert solver.pop(index) == values.pop(index)
        elif kind == 2:
            solver.reverse_range(left, right)
            values[left:right] = values[left:right][::-1]
        elif kind == 3:
            action = (rng.randrange(mod), rng.randrange(mod))
            solver.apply(left, right, action)
            values[left:right] = [(action[0] * x + action[1]) % mod for x in values[left:right]]
        elif kind == 4:
            assert solver.prod(left, right) == sum(values[left:right]) % mod
        else:
            index = rng.randrange(len(values))
            value = rng.randrange(mod)
            solver.set(index, value)
            values[index] = value
        assert solver.prod() == sum(values) % mod
    assert solver.to_list() == values


def test_implicit_treap_deep_build_without_recursion():
    size = 200000
    solver = ImplicitTreap(range(size))
    assert len(solver) == size
    assert solver.prod() == size * (size - 1) // 2
    solver.reverse(0, size)
    assert solver[0] == size - 1
    assert solver[-1] == 0


def test_noncommutative_product_with_lazy_assignment():
    rng = random.Random(80199)
    values = list("abracadabra")
    solver = ImplicitTreap(values, lambda a, b: a + b, "",
                           lambda f, x, n: f * n, lambda f, g: f)
    for _ in range(3000):
        left = rng.randrange(len(values) + 1)
        right = rng.randrange(left, len(values) + 1)
        kind = rng.randrange(4)
        if kind == 0:
            char = rng.choice("abc")
            solver.apply(left, right, char)
            values[left:right] = [char] * (right - left)
        elif kind == 1:
            solver.reverse_range(left, right)
            values[left:right] = values[left:right][::-1]
        elif kind == 2:
            assert solver.prod(left, right) == "".join(values[left:right])
        else:
            solver.insert(left, "d")
            values.insert(left, "d")
            index = rng.randrange(len(values))
            assert solver.pop(index) == values.pop(index)
        assert solver.prod() == "".join(values)


def test_none_is_a_valid_lazy_action():
    solver = ImplicitTreap([1, 2, 3], mapping=lambda f, x, n: 0 if f is None else f * n,
                           composition=lambda f, g: f, commutative=True)
    solver.apply(0, 3, None)
    assert solver.prod() == 0
    solver.reverse_range(0, 3)
    assert solver.tolist() == [0, 0, 0]
    solver.apply(1, 3, 7)
    solver.apply(2, 3, None)
    assert solver.tolist() == [0, 7, 0]
    assert solver.prod() == 7
