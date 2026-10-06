"""等比数列上の多点評価と補間を計算する。"""

from library_codex.fps.FormalPowerSeries import DEFAULT_MOD, fps_multiply
from library_codex.convolution.MiddleProduct import middle_product

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
    if initial == 0:
        return [polynomial[0] % mod] * count
    if ratio == 1 or count == 1:
        value = 0
        for coefficient in reversed(polynomial):
            value = (value * initial + coefficient) % mod
        return [value] * count
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
    product = middle_product(triangular, weighted, mod)
    return [
        product[index] * inverse_triangular[index] % mod
        for index in range(count)
    ]

def interpolate_geometric(values, initial, ratio, mod=DEFAULT_MOD):
    """Interpolate f from f(initial*ratio**i); points must be distinct."""
    size = len(values)
    if size < 2:
        return [value % mod for value in values]
    initial %= mod
    ratio %= mod
    if not initial or ratio == 1:
        raise ValueError("interpolation points must be distinct modulo mod")
    if ratio == 0:
        if size != 2:
            raise ValueError("interpolation points must be distinct modulo mod")
        return [values[1] % mod, (values[0] - values[1]) * pow(initial, -1, mod) % mod]
    triangular = [1] * (2 * size - 1)
    products = [1] * size
    power = ratio
    for index in range(1, size):
        products[index] = products[index - 1] * (1 - power) % mod
        power = power * ratio % mod
    if not products[-1]:
        raise ValueError("interpolation points must be distinct modulo mod")
    full_product = products[-1] * (1 - power) % mod
    inverse_products = [1] * size
    inverse_products[-1] = pow(products[-1], -1, mod)
    inverse_ratio = pow(ratio, -1, mod)
    for index in range(size - 1, 0, -1):
        power = power * inverse_ratio % mod
        inverse_products[index - 1] = inverse_products[index] * (1 - power) % mod
    power = 1
    for index in range(1, len(triangular)):
        triangular[index] = triangular[index - 1] * power % mod
        power = power * ratio % mod
    inverse_triangular = [1] * size
    power = 1
    for index in range(1, size):
        inverse_triangular[index] = inverse_triangular[index - 1] * power % mod
        power = power * inverse_ratio % mod
    weighted = [0] * size
    scale = inverse_triangular[-1]
    for index in range(size):
        value = (values[index] * triangular[size - 1 - index] % mod
                 * scale % mod * inverse_products[index] % mod
                 * inverse_products[size - 1 - index] % mod
                 * inverse_triangular[index] % mod)
        weighted[index] = -value % mod if index & 1 else value
    rational = middle_product(triangular, weighted, mod)
    for index in range(size):
        rational[index] = rational[index] * inverse_triangular[index] % mod
    denominator = [1] * size
    for index in range(1, size):
        value = (triangular[index] * full_product % mod
                 * inverse_products[index] % mod * inverse_products[size - index] % mod)
        denominator[index] = -value % mod if index & 1 else value
    result = fps_multiply(rational, denominator, mod)[:size]
    result.reverse()
    inverse_initial = pow(initial, -1, mod)
    power = 1
    for index in range(size):
        result[index] = result[index] * power % mod
        power = power * inverse_initial % mod
    return result

