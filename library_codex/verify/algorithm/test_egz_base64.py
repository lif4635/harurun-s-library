import itertools
import random

from library_codex.algorithm.Base64Integers import decode_integers, encode_integers
from library_codex.algorithm.MiscAlgorithms import erdos_ginzburg_ziv_indices


def test_egz_random_and_exhaustive_small():
    rng = random.Random(81)
    for order in range(1, 100):
        for _ in range(20):
            values = [rng.randrange(-10000, 10001) for _ in range(2 * order - 1)]
            indices = erdos_ginzburg_ziv_indices(order, values)
            assert len(indices) == order and len(set(indices)) == order
            assert sum(values[index] for index in indices) % order == 0
    for order in range(1, 5):
        for values in itertools.product(range(order), repeat=2 * order - 1):
            indices = erdos_ginzburg_ziv_indices(order, values)
            assert sum(values[index] for index in indices) % order == 0


def test_base64_integer_roundtrip():
    rng = random.Random(82)
    for size in range(1, 100):
        values = [rng.randrange(1 << rng.randrange(1, 63)) for _ in range(size)]
        assert decode_integers(encode_integers(values)) == values
        signed = [rng.randrange(-(1 << 63), 1 << 63) for _ in range(size)]
        signed[0] = -abs(signed[0]) - (signed[0] == 0)
        assert decode_integers(encode_integers(signed), signed=True) == signed
