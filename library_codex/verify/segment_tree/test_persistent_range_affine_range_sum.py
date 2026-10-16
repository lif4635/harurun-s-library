import random

import pytest

from library_codex.segment_tree.PersistentRangeAffineRangeSum import PersistentRangeAffineRangeSum


def test_branching_versions_against_arrays():
    rng = random.Random(226)
    for mod in (1, 12, 998244353):
        for n in (0, 1, 2, 3, 7, 16, 31):
            values = [rng.randrange(-100, 100) for _ in range(n)]
            tree = PersistentRangeAffineRangeSum(values, mod)
            versions = [[v % mod for v in values]]
            for _ in range(150):
                base = rng.randrange(len(versions))
                left, right = sorted((rng.randrange(n + 1), rng.randrange(n + 1)))
                expected = versions[base][:]
                if rng.randrange(2):
                    b, c = rng.randrange(-3, 4), rng.randrange(-10, 11)
                    version = tree.apply(left, right, b, c, base)
                    expected[left:right] = [(b * v + c) % mod for v in expected[left:right]]
                else:
                    source = rng.randrange(len(versions))
                    version = tree.copy(left, right, source, base)
                    expected[left:right] = versions[source][left:right]
                assert version == len(versions)
                versions.append(expected)
                assert tree.tolist(version) == expected
                assert tree.tolist(base) == versions[base]
                assert tree.prod(left, right, version) == sum(expected[left:right]) % mod
                assert tree.prod(0, n, base) == sum(versions[base]) % mod
            for version, expected in enumerate(versions):
                assert tree.tolist(version) == expected


def test_zero_multiplier_composition_and_copy():
    tree = PersistentRangeAffineRangeSum([1, 2, 3, 4, 5])
    a = tree.apply(0, 5, 0, 7, 0)
    b = tree.apply(1, 4, 3, 2, a)
    c = tree.copy(2, 5, 0, b)
    assert tree.tolist(a) == [7] * 5
    assert tree.tolist(b) == [7, 23, 23, 23, 7]
    assert tree.tolist(c) == [7, 23, 3, 4, 5]
    assert tree.get(1) == 23
    assert str(tree) == "[7, 23, 3, 4, 5]"
    assert repr(tree) == "PersistentRangeAffineRangeSum([7, 23, 3, 4, 5], mod=998244353)"
    assert len(tree) == 5


def test_query_does_not_allocate_and_full_copy_shares_storage():
    tree = PersistentRangeAffineRangeSum(range(1024))
    a = tree.apply(0, 1024, 3, 7)
    size = len(tree._sum)
    b = tree.copy(0, 1024, 0, a)
    assert len(tree._sum) == size
    assert tree.prod(23, 941, b) == sum(range(23, 941))
    tree.tolist(a)
    assert len(tree._sum) == size
    tree.apply(321, 654, 2, 9, a)
    assert len(tree._sum) - size <= 20


def test_invalid_ranges_and_versions():
    with pytest.raises(ValueError):
        PersistentRangeAffineRangeSum([], 0)
    tree = PersistentRangeAffineRangeSum([1, 2])
    for left, right in ((-1, 1), (0, 3), (2, 1)):
        with pytest.raises(IndexError):
            tree.apply(left, right, 1, 2)
        with pytest.raises(IndexError):
            tree.copy(left, right, 0)
        with pytest.raises(IndexError):
            tree.prod(left, right)
    with pytest.raises(IndexError):
        tree.prod(0, 2, 1)
    assert len(tree.roots) == 1
