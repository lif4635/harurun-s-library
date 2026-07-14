import random

from library_codex.math.Nimber import Nimber, NimberToField, nim_product


def _naive_table(limit):
    table = [[0] * limit for _ in range(limit)]
    for first in range(1, limit):
        for second in range(first, limit):
            reachable = set()
            for left in range(first):
                for right in range(second):
                    reachable.add(table[left][second] ^ table[first][right]
                                  ^ table[left][right])
            value = 0
            while value in reachable:
                value += 1
            table[first][second] = table[second][first] = value
    return table


def test_nimber_product_against_mex_and_field_axioms():
    naive = _naive_table(32)
    for first in range(32):
        for second in range(32):
            assert nim_product(first, second, 8) == naive[first][second]
    rng = random.Random(689)
    for bits in (8, 16, 32, 64):
        mask = (1 << bits) - 1
        for _ in range(1000):
            a = Nimber(rng.getrandbits(bits), bits)
            b = Nimber(rng.getrandbits(bits), bits)
            c = Nimber(rng.getrandbits(bits), bits)
            assert a * b == b * a
            assert a * (b + c) == a * b + a * c
            assert (a * b) * c == a * (b * c)
            assert a * 1 == a
            if int(a):
                assert a * a.inv() == 1


def test_nimber_field_basis_round_trip():
    # The first eight powers of 16 form a polynomial basis in this tower.
    converter = NimberToField(Nimber(16, 8))
    for value in range(256):
        assert int(converter.field2nimber(converter.nimber2field(value))) == value
