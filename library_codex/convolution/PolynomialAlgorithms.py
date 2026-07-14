from heapq import heapify, heappop, heappush

from library_codex.convolution.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_derivative,
    fps_divmod,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
    fps_remainder,
    fps_shrink,
    fps_subtract,
    fps_taylor_shift,
)
from library_codex.convolution.MultipointEvaluation import ProductTree


def polynomial_monic(polynomial, mod=DEFAULT_MOD):
    result = fps_shrink(polynomial, mod)
    if not result:
        return []
    inverse = pow(result[-1], -1, mod)
    return [value * inverse % mod for value in result]


def polynomial_gcd(first, second, mod=DEFAULT_MOD):
    first = fps_shrink(first, mod)
    second = fps_shrink(second, mod)
    while second:
        first, second = second, fps_remainder(first, second, mod)
    return polynomial_monic(first, mod)


def polynomial_extended_gcd(first, second, mod=DEFAULT_MOD):
    """Return monic g, s, t satisfying s * first + t * second = g."""
    old_remainder = fps_shrink(first, mod)
    remainder = fps_shrink(second, mod)
    old_first, current_first = [1], []
    old_second, current_second = [], [1]
    while remainder:
        quotient, next_remainder = fps_divmod(old_remainder, remainder, mod)
        old_remainder, remainder = remainder, next_remainder
        old_first, current_first = current_first, fps_subtract(
            old_first, fps_multiply(quotient, current_first, mod), mod
        )
        old_second, current_second = current_second, fps_subtract(
            old_second, fps_multiply(quotient, current_second, mod), mod
        )
        old_first = fps_shrink(old_first, mod)
        old_second = fps_shrink(old_second, mod)
        current_first = fps_shrink(current_first, mod)
        current_second = fps_shrink(current_second, mod)
    if not old_remainder:
        return [], [], []
    scale = pow(old_remainder[-1], -1, mod)
    return (
        [value * scale % mod for value in old_remainder],
        [value * scale % mod for value in old_first],
        [value * scale % mod for value in old_second],
    )


def polynomial_inverse_mod(polynomial, modulus, mod=DEFAULT_MOD):
    modulus = fps_shrink(modulus, mod)
    if len(modulus) <= 1:
        raise ValueError("the polynomial modulus must have positive degree")
    gcd, inverse, _ = polynomial_extended_gcd(polynomial, modulus, mod)
    if gcd != [1]:
        raise ZeroDivisionError("polynomial is not invertible modulo modulus")
    return fps_remainder(inverse, modulus, mod)


def polynomial_pow_mod(polynomial, exponent, modulus, mod=DEFAULT_MOD):
    if exponent < 0:
        polynomial = polynomial_inverse_mod(polynomial, modulus, mod)
        exponent = -exponent
    modulus = fps_shrink(modulus, mod)
    if len(modulus) <= 1:
        raise ValueError("the polynomial modulus must have positive degree")
    result = [1]
    base = fps_remainder(polynomial, modulus, mod)
    while exponent:
        if exponent & 1:
            result = fps_remainder(fps_multiply(result, base, mod), modulus, mod)
        exponent >>= 1
        if exponent:
            base = fps_remainder(fps_multiply(base, base, mod), modulus, mod)
    return result


def polynomial_resultant(first, second, mod=DEFAULT_MOD):
    """Resultant over a field, computed by an iterative Euclidean chain."""
    first = fps_shrink(first, mod)
    second = fps_shrink(second, mod)
    if not first:
        return 1 if len(second) == 1 else 0
    if not second:
        return 1 if len(first) == 1 else 0
    result = 1
    sign = 0
    while True:
        _, remainder = fps_divmod(first, second, mod)
        first_degree = len(first) - 1
        second_degree = len(second) - 1
        if not remainder:
            if second_degree == 0:
                result = result * pow(second[0], first_degree, mod) % mod
            else:
                result = 0
            break
        remainder_degree = len(remainder) - 1
        if first_degree & second_degree & 1:
            sign ^= 1
        result = result * pow(
            second[-1], first_degree - remainder_degree, mod
        ) % mod
        first, second = second, remainder
    return -result % mod if sign else result


def _divide_linear(polynomial, root, mod):
    degree = len(polynomial) - 1
    quotient = [0] * degree
    quotient[-1] = polynomial[-1] % mod
    for index in range(degree - 2, -1, -1):
        quotient[index] = (
            polynomial[index + 1] + root * quotient[index + 1]
        ) % mod
    remainder = (polynomial[0] + root * quotient[0]) % mod
    return fps_shrink(quotient, mod), remainder


def polynomial_roots(polynomial, mod=DEFAULT_MOD, multiplicity=False):
    """Find roots in the prime field. The default result has distinct roots."""
    source = fps_shrink(polynomial, mod)
    if not source:
        raise ValueError("the zero polynomial has every field element as a root")
    if len(source) == 1:
        return []
    if mod <= 4096:
        roots = []
        for value in range(mod):
            evaluated = 0
            for coefficient in reversed(source):
                evaluated = (evaluated * value + coefficient) % mod
            if evaluated == 0:
                roots.append(value)
    elif mod == 2:
        roots = []
        if source[0] % 2 == 0:
            roots.append(0)
        if sum(source) & 1 == 0:
            roots.append(1)
    else:
        x = [0, 1]
        linear_part = polynomial_gcd(
            source,
            fps_subtract(polynomial_pow_mod(x, mod, source, mod), x, mod),
            mod,
        )
        roots = []
        stack = [linear_part] if len(linear_part) > 1 else []
        state = 58
        while stack:
            factor = stack.pop()
            if len(factor) == 2:
                roots.append(-factor[0] * pow(factor[1], -1, mod) % mod)
                continue
            split = []
            while len(split) <= 1 or len(split) == len(factor):
                state = (state * 6364136223846793005 + 1442695040888963407) & (
                    (1 << 64) - 1
                )
                candidate = [state % mod, 1]
                half_power = polynomial_pow_mod(
                    candidate, (mod - 1) >> 1, factor, mod
                )
                split = polynomial_gcd(
                    factor, fps_subtract(half_power, [1], mod), mod
                )
            quotient, remainder = fps_divmod(factor, split, mod)
            if remainder:
                raise ArithmeticError("finite-field factor split failed")
            stack.append(polynomial_monic(split, mod))
            stack.append(polynomial_monic(quotient, mod))
        roots.sort()
    if not multiplicity:
        return roots
    answer = []
    remaining = source
    for root in roots:
        while len(remaining) > 1:
            quotient, remainder = _divide_linear(remaining, root, mod)
            if remainder:
                break
            answer.append(root)
            remaining = quotient
    return answer


def partial_fraction_distinct(numerator, roots, mod=DEFAULT_MOD):
    """Coefficients a_i for f(x) / product(x-b_i) = sum a_i/(x-b_i)."""
    tree = ProductTree(roots, mod)
    if len(numerator) > len(roots):
        raise ValueError("numerator degree must be smaller than denominator degree")
    numerator_values = tree.evaluate(numerator)
    derivative_values = tree.evaluate(fps_derivative(tree.polynomial, mod))
    result = [0] * len(roots)
    for index, denominator in enumerate(derivative_values):
        if denominator == 0:
            raise ValueError("roots must be distinct modulo mod")
        result[index] = numerator_values[index] * pow(denominator, -1, mod) % mod
    return result


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


def polynomial_prefix_sum(polynomial, mod=DEFAULT_MOD, inclusive=False):
    """Polynomial g with g(n)=sum(f(i), 0 <= i < n), or through n if inclusive."""
    polynomial = fps_shrink(polynomial, mod)
    if not polynomial:
        return []
    size = len(polynomial) + 1
    points = list(range(size))
    values = ProductTree(points, mod).evaluate(polynomial)
    samples = [0] * size
    for index in range(1, size):
        samples[index] = (samples[index - 1] + values[index - 1]) % mod
    result = ProductTree(points, mod).interpolate(samples)
    result = fps_shrink(result, mod)
    if inclusive:
        result = fps_taylor_shift(result, 1, mod)
    return fps_shrink(result, mod)


poly_gcd = polynomial_gcd
poly_extgcd = polynomial_extended_gcd
poly_inv_mod = polynomial_inverse_mod
poly_pow_mod = polynomial_pow_mod
resultant = polynomial_resultant
root_finding = polynomial_roots
