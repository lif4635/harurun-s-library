import random

from library_codex.segment_tree.DualSegTree import DualSegTree


def mapping(action, value):
    a, b = action
    return (a * value + b) % 998244353


def composition(new, old):
    a, b = new
    c, d = old
    return a * c % 998244353, (a * d + b) % 998244353


def test_nested_noncommutative_updates():
    tree = DualSegTree(mapping, composition, (1, 0), [1, 2, 3, 4])
    tree.apply(0, 4, (2, 1))
    tree.apply(0, 1, (3, 4))
    tree.apply(1, 3, (0, 7))
    tree.apply(2, 2, (0, 99))
    assert tree.tolist() == [13, 7, 7, 9]


def test_random_affine_updates_and_assignment():
    rng = random.Random(87215)
    for n in (0, 1, 2, 3, 7, 8, 9, 31, 32, 33):
        values = [rng.randrange(100) for _ in range(n)]
        tree = DualSegTree(mapping, composition, (1, 0), values)
        for _ in range(1000):
            if n and rng.randrange(5) == 0:
                i = rng.randrange(n)
                assert tree.get(i) == values[i]
                values[i] = rng.randrange(100)
                tree.set(i, values[i])
            else:
                left = rng.randrange(n + 1)
                right = rng.randrange(left, n + 1)
                action = rng.randrange(10), rng.randrange(10)
                tree.apply(left, right, action)
                for i in range(left, right):
                    values[i] = mapping(action, values[i])
        assert tree.tolist() == values


def test_addition_and_debug_output():
    rng = random.Random(490213)
    values = [rng.randrange(-50, 51) for _ in range(100)]
    tree = DualSegTree(lambda action, value: value + action,
                       lambda new, old: new + old, 0, values)
    for _ in range(10000):
        if rng.randrange(3):
            left = rng.randrange(101)
            right = rng.randrange(left, 101)
            delta = rng.randrange(-30, 31)
            tree.apply(left, right, delta)
            for i in range(left, right):
                values[i] += delta
        else:
            i = rng.randrange(100)
            assert tree.get(i) == values[i]
            values[i] = rng.randrange(-50, 51)
            tree.set(i, values[i])
        if rng.randrange(100) == 0:
            assert tree.tolist() == values
            assert str(tree) == str(values)
            assert repr(tree) == "DualSegTree(%r)" % values
