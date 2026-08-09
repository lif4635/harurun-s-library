"""998244353上の形式的冪級数を昇べき順の係数listで計算する。

`a[i]`は$x^i$の係数を表す。inv・log・exp・pow・sqrt、微分・積分、
多項式除算、Taylor shift、一括積を固定modのradix-4 NTTで計算する。
入力listは変更せず、新しい係数listを返す。
"""

from heapq import heapify, heappop, heappush

from library_codex.convolution.NTT998 import (
    MOD,
    _butterfly,
    _check_length,
    _intt,
    multiply,
)


_INVERSES = [0, 1]
_SPARSE_INV_THRESHOLD = 160
_SPARSE_DIV_THRESHOLD = 200
_SPARSE_LOG_THRESHOLD = 200
_SPARSE_EXP_THRESHOLD = 320
_SPARSE_POWER_THRESHOLD = 32


def _mod_sqrt(value):
    value %= MOD
    if value < 2:
        return value
    if pow(value, (MOD - 1) >> 1, MOD) != 1:
        return -1
    odd = MOD - 1
    exponent = 0
    while odd & 1 == 0:
        odd >>= 1
        exponent += 1
    nonresidue = 3
    root = pow(value, (odd + 1) >> 1, MOD)
    remainder = pow(value, odd, MOD)
    generator = pow(nonresidue, odd, MOD)
    level = exponent
    while remainder != 1:
        position = 1
        squared = remainder * remainder % MOD
        while position < level and squared != 1:
            squared = squared * squared % MOD
            position += 1
        if position == level:
            return -1
        adjustment = pow(generator, 1 << (level - position - 1), MOD)
        root = root * adjustment % MOD
        adjustment = adjustment * adjustment % MOD
        remainder = remainder * adjustment % MOD
        generator = adjustment
        level = position
    return min(root, MOD - root)


def _degree(degree, default):
    if degree is None:
        return default
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    return degree


def _inverses(size):
    if size >= MOD:
        raise ValueError("formal integration requires degree < 998244353")
    values = _INVERSES
    for index in range(len(values), size + 1):
        values.append(-values[MOD % index] * (MOD // index) % MOD)
    return values


def _sparse_terms(series, degree, threshold):
    terms = []
    for index in range(1, min(len(series), degree)):
        value = series[index] % MOD
        if value:
            terms.append((index, value))
            if len(terms) > threshold:
                return None
    return terms


def _fps_inv_sparse(series, degree, first_inverse, terms):
    result = [0] * degree
    result[0] = first_inverse
    for index in range(1, degree):
        total = 0
        for offset, coefficient in terms:
            if offset > index:
                break
            total += coefficient * result[index - offset]
        result[index] = -total * first_inverse % MOD
    return result


def _fps_div_sparse(numerator, degree, first_inverse, terms):
    result = [0] * degree
    for index in range(degree):
        total = numerator[index] % MOD if index < len(numerator) else 0
        for offset, coefficient in terms:
            if offset > index:
                break
            total -= coefficient * result[index - offset]
        result[index] = total * first_inverse % MOD
    return result


def _fps_log_sparse(series, degree, terms):
    inverse = _inverses(degree)
    result = [0] * degree
    for index in range(1, degree):
        total = index * (series[index] % MOD) if index < len(series) else 0
        for offset, coefficient in terms:
            if offset >= index:
                break
            total -= (
                (index - offset) * coefficient * result[index - offset]
            )
        result[index] = total * inverse[index] % MOD
    return result


def _fps_exp_sparse(degree, terms):
    inverse = _inverses(degree)
    result = [0] * degree
    result[0] = 1
    for index in range(1, degree):
        total = 0
        for offset, coefficient in terms:
            if offset > index:
                break
            total += offset * coefficient * result[index - offset]
        result[index] = total * inverse[index] % MOD
    return result


def _fps_power_unit_sparse(degree, exponent, terms):
    inverse = _inverses(degree)
    result = [0] * degree
    result[0] = 1
    exponent %= MOD
    for index in range(1, degree):
        total = 0
        for offset, coefficient in terms:
            if offset > index:
                break
            factor = (exponent * offset - index + offset) % MOD
            total += factor * coefficient * result[index - offset]
        result[index] = total * inverse[index] % MOD
    return result


def shrink(series):
    """係数をmodで正規化し、末尾の0を除いた新しいlistを返す。O(N)。"""

    result = [value % MOD for value in series]
    while result and result[-1] == 0:
        result.pop()
    return result


def fps_add(first, second):
    """2つのFPSを係数ごとに加え、長い方と同じ長さのlistを返す。O(N)。"""

    size = max(len(first), len(second))
    result = [0] * size
    common = min(len(first), len(second))
    mod = MOD
    for index in range(common):
        result[index] = (first[index] + second[index]) % mod
    for index in range(common, len(first)):
        result[index] = first[index] % mod
    for index in range(common, len(second)):
        result[index] = second[index] % mod
    return result


def fps_sub(first, second):
    """`first-second`の係数列を長い方と同じ長さで返す。O(N)。"""

    size = max(len(first), len(second))
    result = [0] * size
    common = min(len(first), len(second))
    mod = MOD
    for index in range(common):
        result[index] = (first[index] - second[index]) % mod
    for index in range(common, len(first)):
        result[index] = first[index] % mod
    for index in range(common, len(second)):
        result[index] = -second[index] % mod
    return result


def fps_neg(series):
    """各係数の加法逆元を同じ長さのlistで返す。O(N)。"""

    return [-value % MOD for value in series]


def fps_diff(series):
    """形式微分の係数を昇べき順で返す。O(N)。"""

    mod = MOD
    return [index * series[index] % mod for index in range(1, len(series))]


def fps_integral(series):
    """定数項を0とした形式積分の係数を昇べき順で返す。O(N)。"""

    inverse = _inverses(len(series))
    mod = MOD
    result = [0] * (len(series) + 1)
    for index, value in enumerate(series, 1):
        result[index] = value * inverse[index] % mod
    return result


def fps_eval(series, value):
    """FPSを多項式とみなし`value`へ代入した値を返す。O(N)。"""

    result = 0
    value %= MOD
    mod = MOD
    for coefficient in reversed(series):
        result = (result * value + coefficient) % mod
    return result


def _inverse_step(series, result, current, target):
    size = current << 1
    mod = MOD
    left = [value % mod for value in series[:target]]
    left.extend([0] * (size - len(left)))
    right = result + [0] * (size - current)
    _butterfly(left)
    _butterfly(right)
    for index in range(size):
        left[index] = left[index] * right[index] % mod
    _intt(left)
    for index in range(current):
        left[index] = 0
    for index in range(current, target):
        left[index] = -left[index] % mod
    for index in range(target, size):
        left[index] = 0
    _butterfly(left)
    for index in range(size):
        left[index] = left[index] * right[index] % mod
    _intt(left)
    result.extend(left[current:target])


def fps_inv(series, degree=None):
    r"""$1/f(x)\bmod x^{degree}$の係数を`degree`個返す。O(N log N)。"""

    degree = _degree(degree, len(series))
    if degree == 0:
        return []
    if not series or series[0] % MOD == 0:
        raise ZeroDivisionError("fps inverse requires nonzero constant coefficient")
    first_inverse = pow(series[0] % MOD, MOD - 2, MOD)
    terms = _sparse_terms(series, degree, _SPARSE_INV_THRESHOLD)
    if terms is not None:
        return _fps_inv_sparse(series, degree, first_inverse, terms)
    result = [first_inverse]
    current = 1
    while current < degree:
        target = min(current << 1, degree)
        _check_length(current << 1)
        _inverse_step(series, result, current, target)
        current = target
    return result


def fps_div(numerator, denominator, degree=None):
    r"""Return ``numerator / denominator mod x^degree``. O(N log N)."""

    degree = _degree(degree, len(numerator))
    if degree == 0:
        return []
    if not denominator or denominator[0] % MOD == 0:
        raise ZeroDivisionError("fps division requires nonzero denominator constant")
    first_inverse = pow(denominator[0] % MOD, MOD - 2, MOD)
    terms = _sparse_terms(
        denominator, degree, _SPARSE_DIV_THRESHOLD
    )
    if terms is not None:
        return _fps_div_sparse(
            numerator, degree, first_inverse, terms
        )
    inverse = fps_inv(denominator, degree)
    result = multiply(numerator[:degree], inverse)[:degree]
    result.extend([0] * (degree - len(result)))
    return result


def fps_log(series, degree=None):
    r"""$\log f(x)\bmod x^{degree}$を返す。`f[0]`は1。O(N log N)。"""

    degree = _degree(degree, len(series))
    if degree == 0:
        return []
    if not series or series[0] % MOD != 1:
        raise ValueError("fps logarithm requires constant coefficient 1")
    terms = _sparse_terms(series, degree, _SPARSE_LOG_THRESHOLD)
    if terms is not None:
        return _fps_log_sparse(series, degree, terms)
    product = multiply(fps_diff(series), fps_inv(series, degree))
    result = fps_integral(product[:degree - 1])
    result.extend([0] * (degree - len(result)))
    return result


def _fps_exp_ntt(series, degree):
    mod = MOD
    b = [1, series[1] % mod if len(series) > 1 else 0]
    c = [1]
    z2 = [1, 1]
    inverse = [0, 1]
    size = 2
    while size < degree:
        doubled = size << 1
        y = b + [0] * size
        _butterfly(y)
        z1 = z2
        z = [y[index] * z1[index] % mod for index in range(size)]
        _intt(z)
        for index in range(size >> 1):
            z[index] = 0
        _butterfly(z)
        for index in range(size):
            z[index] = -z[index] * z1[index] % mod
        _intt(z)
        c.extend(z[size >> 1:])
        z2 = c + [0] * size
        _butterfly(z2)

        source_size = min(len(series), size)
        x = [series[index] % mod for index in range(source_size)]
        x.extend([0] * (size - source_size))
        x = fps_diff(x)
        x.append(0)
        _butterfly(x)
        for index in range(size):
            x[index] = x[index] * y[index] % mod
        _intt(x)
        for index in range(1, len(b)):
            x[index - 1] = (x[index - 1] - index * b[index]) % mod
        x.extend([0] * size)
        for index in range(size - 1):
            x[size + index], x[index] = x[index], 0
        _butterfly(x)
        for index in range(doubled):
            x[index] = x[index] * z2[index] % mod
        _intt(x)
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
        _butterfly(x)
        for index in range(doubled):
            x[index] = x[index] * y[index] % mod
        _intt(x)
        b.extend(x[size:])
        size = doubled
    return b[:degree]


def fps_exp(series, degree=None):
    r"""$\exp f(x)\bmod x^{degree}$を返す。`f[0]`は0。O(N log N)。"""

    degree = _degree(degree, len(series))
    if degree == 0:
        return []
    if series and series[0] % MOD:
        raise ValueError("fps exponential requires constant coefficient 0")
    terms = _sparse_terms(series, degree, _SPARSE_EXP_THRESHOLD)
    if terms is not None:
        return _fps_exp_sparse(degree, terms)
    _check_length(1 << (degree - 1).bit_length())
    if degree == 1:
        return [1]
    return _fps_exp_ntt(series, degree)


def fps_pow(series, exponent, degree=None):
    r"""$f(x)^{exponent}\bmod x^{degree}$を係数`degree`個で返す。O(N log N)。"""

    degree = _degree(degree, len(series))
    if degree == 0:
        return []
    if exponent == 0:
        return [1] + [0] * (degree - 1)
    leading = 0
    while leading < len(series) and series[leading] % MOD == 0:
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
    coefficient = series[leading] % MOD
    inverse_coefficient = pow(coefficient, MOD - 2, MOD)
    needed = degree - shift
    normalized = [
        value * inverse_coefficient % MOD for value in series[leading:]
    ]
    terms = _sparse_terms(
        normalized, needed, _SPARSE_POWER_THRESHOLD
    )
    if terms is not None:
        result = _fps_power_unit_sparse(needed, exponent, terms)
    else:
        logarithm = fps_log(normalized, needed)
        for index in range(needed):
            logarithm[index] = logarithm[index] * exponent % MOD
        result = fps_exp(logarithm, needed)
    scale = pow(coefficient, exponent, MOD)
    return [0] * shift + [value * scale % MOD for value in result]


def fps_sqrt(series, degree=None):
    r"""$g(x)^2=f(x)\bmod x^{degree}$となる係数列を返し、なければ`None`。O(N log N)。"""

    degree = _degree(degree, len(series))
    if degree == 0:
        return []
    leading = 0
    limit = min(len(series), degree)
    while leading < limit and series[leading] % MOD == 0:
        leading += 1
    if leading == limit:
        return [0] * degree
    if leading & 1:
        return None
    shift = leading >> 1
    needed = degree - shift
    source = [value % MOD for value in series[leading:]]
    root = _mod_sqrt(source[0])
    if root == -1:
        return None
    inverse_constant = pow(source[0], MOD - 2, MOD)
    normalized = [value * inverse_constant % MOD for value in source]
    terms = _sparse_terms(
        normalized, needed, _SPARSE_POWER_THRESHOLD
    )
    if terms is not None:
        result = _fps_power_unit_sparse(
            needed, (MOD + 1) >> 1, terms
        )
        return [0] * shift + [value * root % MOD for value in result]
    inverse_two = (MOD + 1) >> 1
    result = [root]
    current = 1
    while current < needed:
        target = min(current << 1, needed)
        quotient = multiply(source[:target], fps_inv(result, target))[:target]
        result.extend([0] * (target - len(result)))
        for index in range(target):
            value = quotient[index] if index < len(quotient) else 0
            result[index] = (result[index] + value) * inverse_two % MOD
        current = target
    return [0] * shift + result[:needed]


def taylor_shift(series, shift):
    """$f(x+shift)$の係数を`f`と同じ長さのlistで返す。O(N log N)。"""

    size = len(series)
    if size == 0:
        return []
    factorial = [1] * size
    for index in range(1, size):
        factorial[index] = factorial[index - 1] * index % MOD
    inverse_factorial = [0] * size
    inverse_factorial[-1] = pow(factorial[-1], MOD - 2, MOD)
    for index in range(size - 1, 0, -1):
        inverse_factorial[index - 1] = inverse_factorial[index] * index % MOD
    left = [series[index] * factorial[index] % MOD for index in range(size)]
    left.reverse()
    right = [0] * size
    power = 1
    shift %= MOD
    for index in range(size):
        right[index] = power * inverse_factorial[index] % MOD
        power = power * shift % MOD
    product = multiply(left, right)
    return [
        product[size - 1 - index] * inverse_factorial[index] % MOD
        for index in range(size)
    ]


def fps_product(polynomials):
    """複数の多項式をすべて掛けた係数列を返す。O(S log S log K)。"""

    heap = []
    serial = 0
    for polynomial in polynomials:
        values = [value % MOD for value in polynomial]
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
        product = multiply(first, second)
        heappush(heap, (len(product), serial, product))
        serial += 1
    return heap[0][2]
