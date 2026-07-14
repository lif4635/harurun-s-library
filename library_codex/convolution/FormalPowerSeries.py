from heapq import heapify, heappop, heappush

from library_codex.convolution.NTT import convolution, get_ntt
from library_codex.math.ModularArithmetic import modular_square_root


DEFAULT_MOD = 998244353
_INVERSE_CACHE = {}


def _degree(degree, default):
    if degree is None:
        return default
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    return degree


def _inverses(size, mod):
    if size >= mod:
        raise ValueError("formal integration requires degree < mod")
    values = _INVERSE_CACHE.get(mod)
    if values is None:
        values = [0, 1]
        _INVERSE_CACHE[mod] = values
    for index in range(len(values), size + 1):
        values.append(-values[mod % index] * (mod // index) % mod)
    return values


def fps_shrink(series, mod=DEFAULT_MOD):
    result = [value % mod for value in series]
    while result and result[-1] == 0:
        result.pop()
    return result


def shrink(series, mod=DEFAULT_MOD):
    for index in range(len(series)):
        series[index] %= mod
    while series and series[-1] == 0:
        series.pop()
    return series


def fps_add(first, second, mod=DEFAULT_MOD):
    size = max(len(first), len(second))
    result = [0] * size
    common = min(len(first), len(second))
    for index in range(common):
        result[index] = (first[index] + second[index]) % mod
    for index in range(common, len(first)):
        result[index] = first[index] % mod
    for index in range(common, len(second)):
        result[index] = second[index] % mod
    return result


def fps_subtract(first, second, mod=DEFAULT_MOD):
    size = max(len(first), len(second))
    result = [0] * size
    common = min(len(first), len(second))
    for index in range(common):
        result[index] = (first[index] - second[index]) % mod
    for index in range(common, len(first)):
        result[index] = first[index] % mod
    for index in range(common, len(second)):
        result[index] = -second[index] % mod
    return result


def fps_negate(series, mod=DEFAULT_MOD):
    return [-value % mod for value in series]


def fps_multiply(first, second, mod=DEFAULT_MOD):
    return convolution(first, second, mod)


def fps_derivative(series, mod=DEFAULT_MOD):
    return [index * series[index] % mod for index in range(1, len(series))]


def fps_integral(series, mod=DEFAULT_MOD):
    inverse = _inverses(len(series), mod)
    result = [0] * (len(series) + 1)
    for index, value in enumerate(series, 1):
        result[index] = value * inverse[index] % mod
    return result


def fps_evaluate(series, value, mod=DEFAULT_MOD):
    result = 0
    value %= mod
    for coefficient in reversed(series):
        result = (result * value + coefficient) % mod
    return result


def _inverse_ntt_step(series, result, current, target, transform):
    size = current << 1
    mod = transform.mod
    left = [value % mod for value in series[:target]]
    left.extend([0] * (size - len(left)))
    right = result + [0] * (size - current)
    transform.butterfly(left)
    transform.butterfly(right)
    for index in range(size):
        left[index] = left[index] * right[index] % mod
    transform.butterfly_inv(left)
    for index in range(current):
        left[index] = 0
    for index in range(current, target):
        left[index] = -left[index] % mod
    for index in range(target, size):
        left[index] = 0
    transform.butterfly(left)
    for index in range(size):
        left[index] = left[index] * right[index] % mod
    transform.butterfly_inv(left)
    result.extend(left[current:target])


def fps_inverse(series, degree=None, mod=DEFAULT_MOD):
    degree = _degree(degree, len(series))
    if degree == 0:
        return []
    if not series:
        raise ZeroDivisionError("the zero series is not invertible")
    try:
        first_inverse = pow(series[0] % mod, -1, mod)
    except ValueError as error:
        raise ZeroDivisionError("the constant coefficient is not invertible") from error
    result = [first_inverse]
    current = 1
    transform = None
    try:
        transform = get_ntt(mod)
    except ValueError:
        pass
    while current < degree:
        target = min(current << 1, degree)
        direct = transform is not None
        if direct:
            try:
                transform._check_length(current << 1)
            except ValueError:
                direct = False
        if direct:
            _inverse_ntt_step(series, result, current, target, transform)
        else:
            product = fps_multiply(series[:target], result, mod)[:target]
            correction = [0] * target
            correction[0] = (2 - product[0]) % mod
            for index in range(1, len(product)):
                correction[index] = -product[index] % mod
            result = fps_multiply(result, correction, mod)[:target]
        current = target
    return result


def fps_logarithm(series, degree=None, mod=DEFAULT_MOD):
    degree = _degree(degree, len(series))
    if degree == 0:
        return []
    if not series or series[0] % mod != 1:
        raise ValueError("fps logarithm requires constant coefficient 1")
    product = fps_multiply(
        fps_derivative(series, mod),
        fps_inverse(series, degree, mod),
        mod,
    )
    result = fps_integral(product[:degree - 1], mod)
    result.extend([0] * (degree - len(result)))
    return result


def _fps_exponential_ntt(series, degree, transform):
    mod = transform.mod
    b = [1, series[1] % mod if len(series) > 1 else 0]
    c = [1]
    z2 = [1, 1]
    inverse = [0, 1]
    size = 2
    while size < degree:
        doubled = size << 1
        y = b + [0] * size
        transform.butterfly(y)
        z1 = z2
        z = [y[index] * z1[index] % mod for index in range(size)]
        transform.butterfly_inv(z)
        for index in range(size >> 1):
            z[index] = 0
        transform.butterfly(z)
        for index in range(size):
            z[index] = -z[index] * z1[index] % mod
        transform.butterfly_inv(z)
        c.extend(z[size >> 1:])
        z2 = c + [0] * size
        transform.butterfly(z2)

        source_size = min(len(series), size)
        x = [series[index] % mod for index in range(source_size)]
        x.extend([0] * (size - source_size))
        x = fps_derivative(x, mod)
        x.append(0)
        transform.butterfly(x)
        for index in range(size):
            x[index] = x[index] * y[index] % mod
        transform.butterfly_inv(x)
        for index in range(1, len(b)):
            x[index - 1] = (x[index - 1] - index * b[index]) % mod
        x.extend([0] * size)
        for index in range(size - 1):
            x[size + index], x[index] = x[index], 0
        transform.butterfly(x)
        for index in range(doubled):
            x[index] = x[index] * z2[index] % mod
        transform.butterfly_inv(x)
        x.pop()
        for index in range(len(inverse), len(x) + 1):
            inverse.append(-inverse[mod % index] * (mod // index) % mod)
        x = [0] + [
            value * inverse[index + 1] % mod
            for index, value in enumerate(x)
        ]
        for index in range(size):
            x[index] = 0
        for index in range(size, min(len(series), doubled)):
            x[index] = (x[index] + series[index]) % mod
        transform.butterfly(x)
        for index in range(doubled):
            x[index] = x[index] * y[index] % mod
        transform.butterfly_inv(x)
        b.extend(x[size:])
        size = doubled
    return b[:degree]


def _fps_exponential_newton(series, degree, mod):
    result = [1]
    while len(result) < degree:
        target = min(len(result) << 1, degree)
        logarithm = fps_logarithm(result, target, mod)
        correction = [0] * target
        for index in range(target):
            value = series[index] if index < len(series) else 0
            correction[index] = (value - logarithm[index]) % mod
        correction[0] = (correction[0] + 1) % mod
        result = fps_multiply(result, correction, mod)[:target]
    return result


def fps_exponential(series, degree=None, mod=DEFAULT_MOD):
    degree = _degree(degree, len(series))
    if degree == 0:
        return []
    if series and series[0] % mod:
        raise ValueError("fps exponential requires constant coefficient 0")
    transform = None
    try:
        transform = get_ntt(mod)
        transform._check_length(1 << (degree - 1).bit_length())
    except ValueError:
        transform = None
    if transform is not None:
        return _fps_exponential_ntt(series, degree, transform)
    return _fps_exponential_newton(series, degree, mod)


def fps_power(series, exponent, degree=None, mod=DEFAULT_MOD):
    degree = _degree(degree, len(series))
    if degree == 0:
        return []
    if exponent == 0:
        return [1] + [0] * (degree - 1)
    leading = 0
    while leading < len(series) and series[leading] % mod == 0:
        leading += 1
    if leading == len(series):
        if exponent < 0:
            raise ZeroDivisionError("a zero series cannot have negative exponent")
        return [0] * degree
    if exponent < 0 and leading:
        raise ValueError("negative power requires an invertible series")
    shift = leading * exponent
    if shift >= degree:
        return [0] * degree
    coefficient = series[leading] % mod
    try:
        inverse_coefficient = pow(coefficient, -1, mod)
    except ValueError as error:
        raise ZeroDivisionError("the leading coefficient is not invertible") from error
    needed = degree - shift
    normalized = [
        value * inverse_coefficient % mod for value in series[leading:]
    ]
    logarithm = fps_logarithm(normalized, needed, mod)
    for index in range(needed):
        logarithm[index] = logarithm[index] * exponent % mod
    result = fps_exponential(logarithm, needed, mod)
    scale = pow(coefficient, exponent, mod)
    result = [value * scale % mod for value in result]
    return [0] * shift + result


def fps_square_root(series, degree=None, mod=DEFAULT_MOD):
    degree = _degree(degree, len(series))
    if degree == 0:
        return []
    leading = 0
    limit = min(len(series), degree)
    while leading < limit and series[leading] % mod == 0:
        leading += 1
    if leading == limit:
        return [0] * degree
    if leading & 1:
        return None
    shift = leading >> 1
    needed = degree - shift
    source = [value % mod for value in series[leading:]]
    root = modular_square_root(source[0], mod)
    if root == -1:
        return None
    try:
        inverse_two = pow(2, -1, mod)
    except ValueError as error:
        raise ZeroDivisionError("fps square root requires invertible 2") from error
    result = [root]
    current = 1
    while current < needed:
        target = min(current << 1, needed)
        quotient = fps_multiply(
            source[:target], fps_inverse(result, target, mod), mod
        )[:target]
        result.extend([0] * (target - len(result)))
        for index in range(target):
            value = quotient[index] if index < len(quotient) else 0
            result[index] = (result[index] + value) * inverse_two % mod
        current = target
    return [0] * shift + result[:needed]


def fps_quotient(dividend, divisor, mod=DEFAULT_MOD):
    first = fps_shrink(dividend, mod)
    second = fps_shrink(divisor, mod)
    if not second:
        raise ZeroDivisionError("polynomial division by zero")
    if len(first) < len(second):
        return []
    quotient_size = len(first) - len(second) + 1
    if len(second) <= 64:
        result = [0] * quotient_size
        remainder = first[:]
        try:
            inverse_leading = pow(second[-1], -1, mod)
        except ValueError as error:
            raise ZeroDivisionError("the leading coefficient is not invertible") from error
        width = len(second)
        for index in range(quotient_size - 1, -1, -1):
            value = remainder[index + width - 1] * inverse_leading % mod
            result[index] = value
            for offset in range(width):
                remainder[index + offset] = (
                    remainder[index + offset] - value * second[offset]
                ) % mod
        return result
    reversed_dividend = list(reversed(first[-quotient_size:]))
    reversed_divisor = list(reversed(second))
    result = fps_multiply(
        reversed_dividend,
        fps_inverse(reversed_divisor, quotient_size, mod),
        mod,
    )[:quotient_size]
    result.reverse()
    return result


def fps_divmod(dividend, divisor, mod=DEFAULT_MOD):
    second = fps_shrink(divisor, mod)
    if not second:
        raise ZeroDivisionError("polynomial division by zero")
    first = fps_shrink(dividend, mod)
    quotient = fps_quotient(first, second, mod)
    if not quotient:
        return [], first
    product = fps_multiply(quotient, second, mod)
    remainder = [0] * min(len(second) - 1, max(len(first), len(product)))
    for index in range(len(remainder)):
        left = first[index] if index < len(first) else 0
        right = product[index] if index < len(product) else 0
        remainder[index] = (left - right) % mod
    while remainder and remainder[-1] == 0:
        remainder.pop()
    return quotient, remainder


def fps_remainder(dividend, divisor, mod=DEFAULT_MOD):
    return fps_divmod(dividend, divisor, mod)[1]


def fps_taylor_shift(series, shift, mod=DEFAULT_MOD):
    size = len(series)
    if size == 0:
        return []
    _inverses(size, mod)
    factorial = [1] * size
    for index in range(1, size):
        factorial[index] = factorial[index - 1] * index % mod
    try:
        inverse_factorial = [0] * size
        inverse_factorial[-1] = pow(factorial[-1], -1, mod)
    except ValueError as error:
        raise ZeroDivisionError("factorial is not invertible") from error
    for index in range(size - 1, 0, -1):
        inverse_factorial[index - 1] = (
            inverse_factorial[index] * index % mod
        )
    left = [
        series[index] * factorial[index] % mod
        for index in range(size)
    ]
    left.reverse()
    right = [0] * size
    power = 1
    shift %= mod
    for index in range(size):
        right[index] = power * inverse_factorial[index] % mod
        power = power * shift % mod
    product = fps_multiply(left, right, mod)
    return [
        product[size - 1 - index] * inverse_factorial[index] % mod
        for index in range(size)
    ]


def fps_product(polynomials, mod=DEFAULT_MOD):
    heap = []
    serial = 0
    for polynomial in polynomials:
        values = [value % mod for value in polynomial]
        if not values:
            return []
        heap.append((len(values), serial, values))
        serial += 1
    if not heap:
        return [1]
    heapify(heap)
    while len(heap) > 1:
        _, _, first = heappop(heap)
        _, _, second = heappop(heap)
        product = fps_multiply(first, second, mod)
        heappush(heap, (len(product), serial, product))
        serial += 1
    return heap[0][2]


fps_sub = fps_subtract
fps_neg = fps_negate
fps_mul = fps_multiply
fps_diff = fps_derivative
fps_inv = fps_inverse
fps_log = fps_logarithm
fps_exp = fps_exponential
fps_pow = fps_power
fps_sqrt = fps_square_root
fps_div = fps_quotient
fps_mod = fps_remainder
fps_eval = fps_evaluate
tayler_shift = fps_taylor_shift
