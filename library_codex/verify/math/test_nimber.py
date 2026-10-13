import random
import subprocess
import sys

from library_codex.game.Nimber import Nimber, NimberToField, nim_product
from library_codex.game.Nimber import nim_product16, nim_product32, nim_product64, _EXP16, _LOG16


def test_product64_tables_are_lazy_and_reused():
    source = """
from library_codex.game import Nimber as module
assert not module._EXP16 and not module._LOG16 and not module._CORRECTION16
module.nim_product16(32, 47)
module.nim_product32(65536, 998244353)
module.nim_product64(0, 1 << 63)
module.nim_product64(1, 1 << 63)
assert not module._EXP16
assert module.nim_product64(2, 2) == 3
tables = [module._EXP16, module._LOG16, module._CORRECTION16]
assert list(map(len, tables)) == [131070, 65536, 65536]
module.nim_product64((1 << 64) - 1, (1 << 64) - 1)
assert list(map(len, tables)) == [131070, 65536, 65536]
"""
    subprocess.run([sys.executable, "-c", source], check=True)


def test_product64_lookup_against_tower_and_basis():
    def tower(a, b):
        ah, al = a >> 32, a & 0xffffffff
        bh, bl = b >> 32, b & 0xffffffff
        low = nim_product32(al, bl)
        mixed = nim_product32(ah ^ al, bh ^ bl)
        return ((mixed ^ low) << 32) ^ nim_product32(nim_product32(ah, bh), 1 << 31) ^ low

    rng = random.Random(645319)
    cases = [(1 << a, 1 << b) for a in range(64) for b in range(64)]
    cases += [(rng.getrandbits(64), rng.getrandbits(64)) for _ in range(2000)]
    cases += [(0, (1 << 64) - 1), (1, (1 << 64) - 1), ((1 << 64) - 1, (1 << 64) - 1)]
    for a, b in cases:
        assert nim_product64(a, b) == tower(a, b)
    assert len(set(_EXP16[:65535])) == 65535
    assert all(_EXP16[_LOG16[value]] == value for value in range(1, 65536))
    for value in range(65536):
        assert nim_product64(value, 32768) == nim_product16(value, 32768)


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
