from math import prod
import random

import pytest

from library_codex.convolution.MultivariateMultiplication import _multiply_prefix, multivariate_multiplication


def _fits(part, whole, base):
    for radix in base:
        if part % radix > whole % radix:
            return False
        part //= radix
        whole //= radix
    return True


def test_products_and_prefixes_against_coefficient_pairs():
    rng = random.Random(471)
    for base in ((), (1,), (1, 3), (3, 1), (3, 5), (5, 3), (7, 17), (17, 7), (2, 3, 5), (1, 2, 3, 1)):
        size = prod(base)
        for mod in (998244353, 101, 49):
            if len(base) > 2 and mod != 998244353:
                continue
            for _ in range(12):
                first = [rng.randrange(-mod, mod) for _ in range(size)]
                second = [rng.randrange(-mod, mod) for _ in range(size)]
                expected = [sum(first[j] * second[i - j] for j in range(i + 1) if _fits(j, i, base)) % mod for i in range(size)]
                assert multivariate_multiplication(first, second, base, mod) == expected
                prefix = rng.randrange(1, size + 1)
                assert _multiply_prefix(first, second, base, mod, prefix) == expected[:prefix]
                short = rng.randrange(1, size + 1)
                truncated = first[:short] + [0] * (size - short)
                expected = [sum(truncated[j] * second[i - j] for j in range(i + 1) if _fits(j, i, base)) % mod for i in range(size)]
                assert _multiply_prefix(first[:short], second, base, mod, prefix) == expected[:prefix]


def test_invalid_shape():
    for base in ((0,), (-1, -1)):
        with pytest.raises(ValueError):
            multivariate_multiplication([1], [1], base)
    with pytest.raises(ValueError):
        multivariate_multiplication([1], [1, 2], (1,))
