"""多項式と指数関数の積の有限和・極限和を計算する。"""

from library_codex.fps.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_exponential,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
)

from library_codex.polynomial.MultipointEvaluation import (
    ProductTree,
    interpolate_consecutive,
)

from library_codex.combinatorics.Combination import Combination

def limit_sum_polynomial_exponential(values, ratio, mod=DEFAULT_MOD):
    """Sum ratio**k*f(k), k >= 0, from consecutive samples of f."""
    if not values:
        raise ValueError("at least one sample is required")
    ratio %= mod
    if ratio == 1:
        raise ValueError("the infinite formal sum requires ratio != 1")
    degree = len(values) - 1
    combination = Combination(degree + 1, mod)
    powers = [1] * (degree + 1)
    for index in range(degree):
        powers[index + 1] = powers[index] * ratio % mod
    accumulated = 0
    answer = 0
    for index in range(degree + 1):
        accumulated = (accumulated + powers[index] * values[index]) % mod
        term = (combination.C(degree + 1, index + 1)
                * powers[degree - index] % mod * accumulated % mod)
        answer += -term if (degree - index) & 1 else term
    return answer % mod * pow(pow(1 - ratio, degree + 1, mod), -1, mod) % mod

def sum_polynomial_exponential(values, ratio, count, mod=DEFAULT_MOD):
    """Sum ratio**k*f(k), 0 <= k < count, from consecutive samples of f."""
    if not values:
        raise ValueError("at least one sample is required")
    if count <= 0:
        return 0
    ratio %= mod
    degree = len(values) - 1
    powers = [1] * (degree + 1)
    prefixes = [0] * (degree + 1)
    for index in range(degree + 1):
        if index:
            powers[index] = powers[index - 1] * ratio % mod
        prefixes[index] = powers[index] * values[index] % mod
        if index:
            prefixes[index] = (prefixes[index] + prefixes[index - 1]) % mod
    last = count - 1
    if ratio == 0:
        return values[0] % mod
    if ratio == 1:
        return interpolate_consecutive(prefixes, last, mod)
    combination = Combination(degree + 1, mod)
    constant = 0
    for index in range(degree + 1):
        term = (combination.C(degree + 1, index + 1)
                * powers[degree - index] % mod * prefixes[index] % mod)
        constant += -term if (degree - index) & 1 else term
    constant %= mod
    constant = constant * pow(pow(1 - ratio, degree + 1, mod), -1, mod) % mod
    inverse_ratio = pow(ratio, -1, mod)
    inverse_power = 1
    adjusted = [0] * (degree + 1)
    for index in range(degree + 1):
        adjusted[index] = (prefixes[index] - constant) * inverse_power % mod
        inverse_power = inverse_power * inverse_ratio % mod
    return (pow(ratio, last, mod)
            * interpolate_consecutive(adjusted, last, mod) + constant) % mod
