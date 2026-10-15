from math import prod
import random

import pytest

from library_codex.convolution.MultidimensionalDFT import multidimensional_dft, multivariate_circular_convolution
from library_codex.convolution.NTT import primitive_root


def _digits(index, base):
    result = []
    for radix in base:
        result.append(index % radix)
        index //= radix
    return result


@pytest.mark.parametrize("mod,base", [
    (2, ()), (2, (1,)), (7, (2, 3)), (13, (3, 2, 2)),
    (97, (1, 3, 1, 4)), (97, (3, 3)), (998244353, (2, 7)),
    (998244353, (2, 2, 2, 2)),
])
def test_circular_against_pairs(mod, base):
    rng = random.Random(111)
    size = prod(base)
    digits = [_digits(i, base) for i in range(size)]
    strides = [prod(base[:i]) for i in range(len(base))]
    for _ in range(100):
        first = [rng.randrange(-mod, 2 * mod) for _ in range(size)]
        second = [rng.randrange(-mod, 2 * mod) for _ in range(size)]
        before = first[:], second[:]
        expected = [0] * size
        for i in range(size):
            for j in range(size):
                index = sum((a + b) % radix * stride for a, b, radix, stride in zip(digits[i], digits[j], base, strides))
                expected[index] += first[i] * second[j]
        assert multivariate_circular_convolution(first, second, base, mod) == [x % mod for x in expected]
        assert (first, second) == before


@pytest.mark.parametrize("mod,base", [(7, (2, 3)), (13, (3, 2, 2)), (97, (4, 3)), (998244353, (2, 7))])
def test_transform_order_and_inverse(mod, base):
    rng = random.Random(112)
    size = prod(base)
    digits = [_digits(i, base) for i in range(size)]
    root = primitive_root(mod)
    roots = [pow(root, (mod - 1) // radix, mod) for radix in base]
    for _ in range(10):
        values = [rng.randrange(mod) for _ in range(size)]
        expected = [sum(values[j] * prod(pow(w, a * b, mod) for w, a, b in zip(roots, digits[i], digits[j])) for j in range(size)) % mod for i in range(size)]
        transformed = multidimensional_dft(values, base, mod=mod)
        assert transformed == expected
        assert multidimensional_dft(transformed, base, True, mod) == values


def test_large_binary_axes():
    base = (2,) * 12
    values = list(range(1 << 12))
    transformed = multidimensional_dft(values, base)
    assert multidimensional_dft(transformed, base, True) == values


def test_invalid_shapes():
    for base in ((0,), (-1,), (3,)):
        with pytest.raises(ValueError):
            multidimensional_dft([1], base)
    with pytest.raises(ValueError):
        multidimensional_dft([1], (2,))
    with pytest.raises(ValueError):
        multidimensional_dft([1], (), mod=1)
    with pytest.raises(ValueError):
        multivariate_circular_convolution([1], [1, 2], (2,))
