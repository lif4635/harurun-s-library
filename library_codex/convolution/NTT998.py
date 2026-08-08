"""998244353 固定の高速NTTと係数畳み込み。

`multiply(first, second)` は2つの昇べき順係数列を畳み込み、長さ
`len(first) + len(second) - 1` の係数列を返す。汎用mod判定、原始根探索、
CRTを通らず、固定したradix-4の変換表だけを使う。
"""

MOD = 998244353
PRIMITIVE_ROOT = 3
MAX_LOG = 23

_IMAG = 911660635
_IIMAG = 86583718
_RATE2 = [
    0, 911660635, 509520358, 369330050, 332049552, 983190778,
    123842337, 238493703, 975955924, 603855026, 856644456,
    131300601, 842657263, 730768835, 942482514, 806263778,
    151565301, 510815449, 503497456, 743006876, 741047443,
    56250497, 867605899, 0,
]
_IRATE2 = [
    0, 86583718, 372528824, 373294451, 645684063, 112220581,
    692852209, 155456985, 797128860, 90816748, 860285882,
    927414960, 354738543, 109331171, 293255632, 535113200,
    308540755, 121186627, 608385704, 438932459, 359477183,
    824071951, 103369235, 0,
]
_RATE3 = [
    0, 372528824, 337190230, 454590761, 816400692, 578227951,
    180142363, 83780245, 6597683, 70046822, 623238099, 183021267,
    402682409, 631680428, 344509872, 689220186, 365017329,
    774342554, 729444058, 102986190, 128751033, 395565204, 0,
]
_IRATE3 = [
    0, 509520358, 929031873, 170256584, 839780419, 282974284,
    395914482, 444904435, 72135471, 638914820, 66769500,
    771127074, 985925487, 262319669, 262341272, 625870173,
    768022760, 859816005, 914661783, 430819711, 272774365,
    530924681, 0,
]
_INVERSE_SIZE = {1: 1}


def _check_length(size):
    if size < 1 or size & (size - 1):
        raise ValueError("NTT length must be a positive power of two")
    if size > 1 << MAX_LOG:
        raise ValueError("NTT length exceeds 2^23")


def _butterfly(values):
    """In-place forward radix-4 NTT without coefficient normalization."""

    size = len(values)
    _check_length(size)
    if size == 1:
        values[0] %= MOD
        return values
    height = (size - 1).bit_length()
    level = 0
    mod = MOD
    imag = _IMAG
    rate2 = _RATE2
    rate3 = _RATE3
    while level < height:
        if height - level == 1:
            width = 1 << (height - level - 1)
            rotation = 1
            for block in range(1 << level):
                offset = block << (height - level)
                for index in range(width):
                    left = values[offset + index]
                    right = values[offset + index + width] * rotation
                    values[offset + index] = (left + right) % mod
                    values[offset + index + width] = (left - right) % mod
                rotation = (
                    rotation * rate2[(~block & -~block).bit_length()] % mod
                )
            level += 1
        else:
            width = 1 << (height - level - 2)
            rotation = 1
            for block in range(1 << level):
                rotation2 = rotation * rotation % mod
                rotation3 = rotation2 * rotation % mod
                offset = block << (height - level)
                for index in range(width):
                    value0 = values[offset + index]
                    value1 = values[offset + index + width] * rotation
                    value2 = values[offset + index + 2 * width] * rotation2
                    value3 = values[offset + index + 3 * width] * rotation3
                    difference = (value1 - value3) % mod * imag
                    values[offset + index] = (
                        value0 + value2 + value1 + value3
                    ) % mod
                    values[offset + index + width] = (
                        value0 + value2 - value1 - value3
                    ) % mod
                    values[offset + index + 2 * width] = (
                        value0 - value2 + difference
                    ) % mod
                    values[offset + index + 3 * width] = (
                        value0 - value2 - difference
                    ) % mod
                rotation = (
                    rotation * rate3[(~block & -~block).bit_length()] % mod
                )
            level += 2
    return values


def _butterfly_inv(values):
    """In-place inverse radix-4 transform without division by the length."""

    size = len(values)
    _check_length(size)
    if size == 1:
        values[0] %= MOD
        return values
    height = (size - 1).bit_length()
    level = height
    mod = MOD
    inverse_imag = _IIMAG
    irate2 = _IRATE2
    irate3 = _IRATE3
    while level:
        if level == 1:
            width = 1 << (height - level)
            rotation = 1
            for block in range(1 << (level - 1)):
                offset = block << (height - level + 1)
                for index in range(width):
                    left = values[offset + index]
                    right = values[offset + index + width]
                    values[offset + index] = (left + right) % mod
                    values[offset + index + width] = (
                        (left - right) * rotation % mod
                    )
                rotation = (
                    rotation * irate2[(~block & -~block).bit_length()] % mod
                )
            level -= 1
        else:
            width = 1 << (height - level)
            rotation = 1
            for block in range(1 << (level - 2)):
                rotation2 = rotation * rotation % mod
                rotation3 = rotation2 * rotation % mod
                offset = block << (height - level + 2)
                for index in range(width):
                    value0 = values[offset + index]
                    value1 = values[offset + index + width]
                    value2 = values[offset + index + 2 * width]
                    value3 = values[offset + index + 3 * width]
                    difference = (value2 - value3) * inverse_imag % mod
                    values[offset + index] = (
                        value0 + value1 + value2 + value3
                    ) % mod
                    values[offset + index + width] = (
                        (value0 - value1 + difference) * rotation % mod
                    )
                    values[offset + index + 2 * width] = (
                        (value0 + value1 - value2 - value3) * rotation2 % mod
                    )
                    values[offset + index + 3 * width] = (
                        (value0 - value1 - difference) * rotation3 % mod
                    )
                rotation = (
                    rotation * irate3[(~block & -~block).bit_length()] % mod
                )
            level -= 2
    return values


def ntt(values):
    """`values`を破壊的に順変換し、同じlistを返す。O(N log N)。"""

    return _butterfly(values)


def _intt(values):
    size = len(values)
    _butterfly_inv(values)
    inverse_size = _INVERSE_SIZE.get(size)
    if inverse_size is None:
        inverse_size = pow(size, MOD - 2, MOD)
        _INVERSE_SIZE[size] = inverse_size
    for index in range(size):
        values[index] = values[index] * inverse_size % MOD
    return values


def intt(values):
    """`values`を破壊的に正規化済み逆変換し、同じlistを返す。O(N log N)。"""

    return _intt(values)


def _multiply_naive(first, second):
    first_size = len(first)
    second_size = len(second)
    if first_size == 0 or second_size == 0:
        return []
    if first_size < second_size:
        first, second = second, first
        first_size, second_size = second_size, first_size
    result = [0] * (first_size + second_size - 1)
    mod = MOD
    for index, left in enumerate(first):
        left %= mod
        if left:
            for offset, right in enumerate(second):
                result[index + offset] += left * right
        if index & 7 == 7:
            start = index
            stop = min(index + second_size, len(result))
            for position in range(start, stop):
                result[position] %= mod
    return [value % mod for value in result]


def multiply(first, second):
    """2つの係数列の積を長さ`len(first)+len(second)-1`で返す。O(N log N)。"""

    first_size = len(first)
    second_size = len(second)
    if first_size == 0 or second_size == 0:
        return []
    if min(first_size, second_size) <= 60:
        return _multiply_naive(first, second)
    output_size = first_size + second_size - 1
    size = 1 << (output_size - 1).bit_length()
    _check_length(size)
    left = [value % MOD for value in first]
    left.extend([0] * (size - first_size))
    _butterfly(left)
    if first is second:
        for index in range(size):
            left[index] = left[index] * left[index] % MOD
    else:
        right = [value % MOD for value in second]
        right.extend([0] * (size - second_size))
        _butterfly(right)
        for index in range(size):
            left[index] = left[index] * right[index] % MOD
    _butterfly_inv(left)
    inverse_size = _INVERSE_SIZE.get(size)
    if inverse_size is None:
        inverse_size = pow(size, MOD - 2, MOD)
        _INVERSE_SIZE[size] = inverse_size
    for index in range(output_size):
        left[index] = left[index] * inverse_size % MOD
    del left[output_size:]
    return left


def square(series):
    """係数列の二乗を長さ`2*len(series)-1`で返す。O(N log N)。"""

    size = len(series)
    if size == 0:
        return []
    if size <= 60:
        result = [0] * (2 * size - 1)
        for index, left in enumerate(series):
            left %= MOD
            result[index << 1] += left * left
            for offset in range(index + 1, size):
                result[index + offset] += 2 * left * series[offset]
        return [value % MOD for value in result]
    return multiply(series, series)
