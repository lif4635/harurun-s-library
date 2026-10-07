import random

from library_codex.linear_algebra.XorBasis import XorBasis


def span(values):
    result = {0}
    for value in values:
        result |= {previous ^ value for previous in tuple(result)}
    return result


def test_intersection_all_small_values_and_nonmutation():
    rng = random.Random(618742)
    for width in range(9):
        for _ in range(200):
            first = [rng.getrandbits(width) for _ in range(rng.randrange(12))]
            second = [rng.getrandbits(width) for _ in range(rng.randrange(12))]
            a = XorBasis(first)
            b = XorBasis(second)
            before_a, before_b = a.basis[:], b.basis[:]
            common = a.intersection(b)
            expected = span(first) & span(second)
            assert span(common.basis) == expected
            assert len(expected) == 1 << len(common)
            assert common.basis == b.intersection(a).basis
            assert common.intersection(common).basis == common.basis
            assert a.basis == before_a and b.basis == before_b
    a = XorBasis([1 << 10000, 3 << 5000, 7])
    b = XorBasis([(1 << 10000) ^ 7, 3 << 5000])
    assert a.intersection(b).basis == b.basis
    assert XorBasis().intersection(a).basis == []
    assert a.intersection(XorBasis()).basis == []
    basis = XorBasis([3, 1, 3])
    assert basis.tolist() == [1, 2]
    assert str(basis) == "[1, 2]"
    assert repr(basis) == "XorBasis([1, 2])"
    values = basis.tolist()
    values.clear()
    assert basis.contains(3)


def test_xor_basis_all_generated_values():
    rng = random.Random(121)
    for n in range(13):
        for _ in range(500):
            values = [rng.randrange(1 << 14) for _ in range(n)]
            basis = XorBasis(values)
            generated = {0}
            for value in values:
                generated |= {x ^ value for x in tuple(generated)}
            ordered = sorted(generated)
            assert len(ordered) == 1 << len(basis)
            assert [basis.kth_smallest(i) for i in range(len(ordered))] == ordered
            for i, value in enumerate(ordered):
                assert basis.contains(value)
                assert basis.rank(value) == i
            for xor in (0, rng.randrange(1 << 14), rng.randrange(1 << 14)):
                transformed = sorted(value ^ xor for value in ordered)
                assert basis.minimum(xor) == transformed[0]
                assert basis.maximum(xor) == transformed[-1]
                assert [basis.xor_kth(xor, i) for i in range(len(ordered))] == transformed


def test_bulk_constructor_matches_incremental():
    rng = random.Random(812373)
    for width in (0, 1, 30, 63, 129, 1024):
        for count in (0, 1, 8, 31, 60, 130):
            values = [rng.getrandbits(width) for _ in range(count)]
            incremental = XorBasis()
            for value in values:
                incremental.insert(value)
            bulk = XorBasis(iter(values))
            assert bulk.basis == incremental.basis
            assert bulk.intersection(bulk).basis == bulk.basis
            duplicate = bulk.intersection(bulk)
            duplicate.basis.clear()
            assert bulk.basis == incremental.basis
