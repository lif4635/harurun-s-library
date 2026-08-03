"""等比数列上の多点評価と補間を計算する。"""

from library_codex.convolution.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_exponential,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
)

from library_codex.convolution.MultipointEvaluation import (
    ProductTree,
    interpolate_consecutive,
)

def multipoint_evaluation_geometric(polynomial, initial, ratio, count,
                                    mod=DEFAULT_MOD):
    """Evaluate f(initial*ratio**i), 0 <= i < count."""
    if count < 0:
        raise ValueError("count must be nonnegative")
    if count == 0:
        return []
    size = len(polynomial)
    if size == 0:
        return [0] * count
    initial %= mod
    ratio %= mod
    if ratio == 0:
        first = 0
        power = 1
        for coefficient in polynomial:
            first = (first + coefficient * power) % mod
            power = power * initial % mod
        return [first] + [polynomial[0] % mod] * (count - 1)
    inverse_ratio = pow(ratio, -1, mod)
    total = size + count - 1
    triangular = [1] * total
    inverse_triangular = [1] * total
    ratio_power = 1
    inverse_power = 1
    for index in range(1, total):
        triangular[index] = triangular[index - 1] * ratio_power % mod
        inverse_triangular[index] = (
            inverse_triangular[index - 1] * inverse_power % mod
        )
        ratio_power = ratio_power * ratio % mod
        inverse_power = inverse_power * inverse_ratio % mod
    weighted = [0] * size
    initial_power = 1
    for index, coefficient in enumerate(polynomial):
        weighted[index] = (
            coefficient * inverse_triangular[index] % mod * initial_power % mod
        )
        initial_power = initial_power * initial % mod
    weighted.reverse()
    product = fps_multiply(weighted, triangular, mod)
    return [
        product[size - 1 + index] * inverse_triangular[index] % mod
        for index in range(count)
    ]

def interpolate_geometric(values, initial, ratio, mod=DEFAULT_MOD):
    """Interpolate f from f(initial*ratio**i); points must be distinct."""
    points = [0] * len(values)
    power = initial % mod
    ratio %= mod
    for index in range(len(values)):
        points[index] = power
        power = power * ratio % mod
    return ProductTree(points, mod).interpolate(values)

