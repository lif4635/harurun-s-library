"""冪和とそのprefix値を計算する。"""

from heapq import heapify, heappop, heappush

from library_codex.fps.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_derivative,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
    fps_shrink,
    fps_subtract,
    fps_taylor_shift,
)

def _truncated_linear_product(values, degree, mod):
    heap = []
    for serial, value in enumerate(values):
        heap.append((2, serial, [1, -value % mod]))
    if not heap:
        return [1]
    heapify(heap)
    serial = len(heap)
    while len(heap) > 1:
        _, _, first = heappop(heap)
        _, _, second = heappop(heap)
        product = fps_multiply(first, second, mod)[:degree]
        heappush(heap, (len(product), serial, product))
        serial += 1
    return heap[0][2][:degree]

def power_sums(values, max_exponent, mod=DEFAULT_MOD):
    """Return sum(value**k) for 0 <= k <= max_exponent."""
    if max_exponent < 0:
        return []
    if max_exponent == 0:
        return [len(values) % mod]
    product = _truncated_linear_product(values, max_exponent + 1, mod)
    logarithm = fps_logarithm(product, max_exponent + 1, mod)
    result = [0] * (max_exponent + 1)
    result[0] = len(values) % mod
    for exponent in range(1, max_exponent + 1):
        result[exponent] = -exponent * logarithm[exponent] % mod
    return result

def prefix_sum_powers(count, max_exponent, mod=DEFAULT_MOD):
    """Return sum(0 <= value < count, value**k) for every k <= max_exponent."""
    if max_exponent < 0:
        return []
    if max_exponent >= mod:
        raise ValueError("max_exponent must be smaller than mod")
    factorial = [1] * (max_exponent + 2)
    for index in range(1, len(factorial)):
        factorial[index] = factorial[index - 1] * index % mod
    inverse_factorial = [1] * len(factorial)
    inverse_factorial[-1] = pow(factorial[-1], -1, mod)
    for index in range(len(factorial) - 1, 0, -1):
        inverse_factorial[index - 1] = inverse_factorial[index] * index % mod
    count %= mod
    numerator = [0] * (max_exponent + 1)
    denominator = [0] * (max_exponent + 1)
    power = count
    for index in range(max_exponent + 1):
        numerator[index] = power * inverse_factorial[index + 1] % mod
        denominator[index] = inverse_factorial[index + 1]
        power = power * count % mod
    quotient = fps_multiply(
        numerator, fps_inverse(denominator, max_exponent + 1, mod), mod
    )[:max_exponent + 1]
    return [quotient[index] * factorial[index] % mod for index in range(len(quotient))]
