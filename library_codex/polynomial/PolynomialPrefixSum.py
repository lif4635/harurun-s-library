"""多項式fから、g(n)=sum(f(i), 0 <= i < n)の係数を求める。"""

from library_codex.fps.FormalPowerSeries import (
    DEFAULT_MOD, fps_inverse, fps_multiply, fps_shrink,
)


def polynomial_prefix_sum(polynomial, mod=DEFAULT_MOD, inclusive=False):
    """Return ascending coefficients of the exclusive or inclusive prefix sum."""
    polynomial = fps_shrink(polynomial, mod)
    if not polynomial:
        return []
    size = len(polynomial)
    if size >= mod:
        raise ValueError("polynomial degree plus one must be smaller than mod")
    factorial = [1] * (size + 1)
    for index in range(1, size + 1):
        factorial[index] = factorial[index - 1] * index % mod
    inverse_factorial = [1] * (size + 1)
    inverse_factorial[size] = pow(factorial[size], -1, mod)
    for index in range(size, 0, -1):
        inverse_factorial[index - 1] = inverse_factorial[index] * index % mod
    bernoulli = fps_inverse(inverse_factorial[1:], size, mod)
    weighted = [polynomial[index] * factorial[index] % mod
                for index in range(size - 1, -1, -1)]
    product = fps_multiply(weighted, bernoulli, mod)
    result = [0] + [product[size - index] * inverse_factorial[index] % mod
                    for index in range(1, size + 1)]
    if inclusive:
        for index, value in enumerate(polynomial):
            result[index] = (result[index] + value) % mod
    return result
