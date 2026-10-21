"""998244353 固定の高速NTTと係数畳み込み。

`multiply(first, second)` は2つの昇べき順係数列を畳み込み、長さ
`len(first) + len(second) - 1` の係数列を返す。汎用mod判定、原始根探索、
CRTを通らず、固定したradix-4の変換表だけを使う。
"""
from array import array as _convolution_ntt998_array
MOD = 998244353
PRIMITIVE_ROOT = 3
MAX_LOG = 23
_convolution_ntt998_IMAG = 911660635
_convolution_ntt998_IIMAG = 86583718
_convolution_ntt998_RATE2 = [0, 911660635, 509520358, 369330050, 332049552, 983190778, 123842337, 238493703, 975955924, 603855026, 856644456, 131300601, 842657263, 730768835, 942482514, 806263778, 151565301, 510815449, 503497456, 743006876, 741047443, 56250497, 867605899, 0]
_convolution_ntt998_IRATE2 = [0, 86583718, 372528824, 373294451, 645684063, 112220581, 692852209, 155456985, 797128860, 90816748, 860285882, 927414960, 354738543, 109331171, 293255632, 535113200, 308540755, 121186627, 608385704, 438932459, 359477183, 824071951, 103369235, 0]
_convolution_ntt998_RATE3 = [0, 372528824, 337190230, 454590761, 816400692, 578227951, 180142363, 83780245, 6597683, 70046822, 623238099, 183021267, 402682409, 631680428, 344509872, 689220186, 365017329, 774342554, 729444058, 102986190, 128751033, 395565204, 0]
_convolution_ntt998_IRATE3 = [0, 509520358, 929031873, 170256584, 839780419, 282974284, 395914482, 444904435, 72135471, 638914820, 66769500, 771127074, 985925487, 262319669, 262341272, 625870173, 768022760, 859816005, 914661783, 430819711, 272774365, 530924681, 0]
_convolution_ntt998_INVERSE_SIZE = {1: 1}

def _convolution_ntt998_check_length(size):
    if size < 1 or size & size - 1:
        raise ValueError('NTT length must be a positive power of two')
    if size > 1 << MAX_LOG:
        raise ValueError('NTT length exceeds 2^23')

def _convolution_ntt998_ntt_plan(size, inverse=False):
    _convolution_ntt998_check_length(size)
    rate2 = _convolution_ntt998_IRATE2 if inverse else _convolution_ntt998_RATE2
    rate3 = _convolution_ntt998_IRATE3 if inverse else _convolution_ntt998_RATE3
    count = max(1, size >> 2)
    first = _convolution_ntt998_array('I', [1]) * count
    second = _convolution_ntt998_array('I', [1]) * count
    third = _convolution_ntt998_array('I', [1]) * count
    rotation = 1
    for block in range(count):
        first[block] = rotation
        second[block] = rotation * rotation % MOD
        third[block] = second[block] * rotation % MOD
        rotation = rotation * rate3[(~block & -~block).bit_length()] % MOD
    count = max(1, size >> 1)
    binary = _convolution_ntt998_array('I', [1]) * count
    rotation = 1
    for block in range(count):
        binary[block] = rotation
        rotation = rotation * rate2[(~block & -~block).bit_length()] % MOD
    return (binary, first, second, third)

def _convolution_ntt998_butterfly(values, tables=None, stride=1):
    """In-place forward radix-4 NTT without coefficient normalization."""
    if stride < 1 or stride & stride - 1 or len(values) % stride:
        raise ValueError('incomplete interleaved NTT lanes')
    size = len(values) // stride
    _convolution_ntt998_check_length(size)
    if size == 1:
        for i in range(stride):
            values[i] %= MOD
        return values
    if tables is not None:
        (binary, first, second, third) = tables
    height = (size - 1).bit_length()
    level = 0
    mod = MOD
    imag = _convolution_ntt998_IMAG
    rate2 = _convolution_ntt998_RATE2
    rate3 = _convolution_ntt998_RATE3
    while level < height:
        if height - level == 1:
            width = stride << height - level - 1
            rotation = 1
            for block in range(1 << level):
                if tables is not None:
                    rotation = binary[block]
                offset = (block << height - level) * stride
                for index in range(width):
                    left = values[offset + index]
                    right = values[offset + index + width] * rotation
                    values[offset + index] = (left + right) % mod
                    values[offset + index + width] = (left - right) % mod
                if tables is None:
                    rotation = rotation * rate2[(~block & -~block).bit_length()] % mod
            level += 1
        else:
            width = stride << height - level - 2
            rotation = 1
            for block in range(1 << level):
                if tables is None:
                    rotation2 = rotation * rotation % mod
                    rotation3 = rotation2 * rotation % mod
                else:
                    rotation = first[block]
                    rotation2 = second[block]
                    rotation3 = third[block]
                offset = (block << height - level) * stride
                for index in range(width):
                    value0 = values[offset + index]
                    value1 = values[offset + index + width] * rotation
                    value2 = values[offset + index + 2 * width] * rotation2
                    value3 = values[offset + index + 3 * width] * rotation3
                    difference = (value1 - value3) % mod * imag
                    values[offset + index] = (value0 + value2 + value1 + value3) % mod
                    values[offset + index + width] = (value0 + value2 - value1 - value3) % mod
                    values[offset + index + 2 * width] = (value0 - value2 + difference) % mod
                    values[offset + index + 3 * width] = (value0 - value2 - difference) % mod
                if tables is None:
                    rotation = rotation * rate3[(~block & -~block).bit_length()] % mod
            level += 2
    return values

def _convolution_ntt998_butterfly_inv(values, tables=None, keep_bit=0, stride=1):
    """In-place inverse radix-4 transform without division by the length."""
    if stride < 1 or stride & stride - 1 or len(values) % stride:
        raise ValueError('incomplete interleaved NTT lanes')
    size = len(values) // stride
    _convolution_ntt998_check_length(size)
    if size == 1:
        for i in range(stride):
            values[i] %= MOD
        return values
    if tables is not None:
        (binary, first, second, third) = tables
    height = (size - 1).bit_length()
    level = height
    keep_bit *= stride
    mod = MOD
    inverse_imag = _convolution_ntt998_IIMAG
    irate2 = _convolution_ntt998_IRATE2
    irate3 = _convolution_ntt998_IRATE3
    while level:
        if level == 1:
            width = stride << height - level
            limited = keep_bit and width > keep_bit
            mask = -keep_bit if limited else 0
            count = width >> bool(limited)
            rotation = 1
            for block in range(1 << level - 1):
                if tables is not None:
                    rotation = binary[block]
                offset = (block << height - level + 1) * stride
                for position in range(count):
                    index = position + (position & mask)
                    left = values[offset + index]
                    right = values[offset + index + width]
                    values[offset + index] = (left + right) % mod
                    values[offset + index + width] = (left - right) * rotation % mod
                if tables is None:
                    rotation = rotation * irate2[(~block & -~block).bit_length()] % mod
            level -= 1
        else:
            width = stride << height - level
            limited = keep_bit and width > keep_bit
            mask = -keep_bit if limited else 0
            count = width >> bool(limited)
            rotation = 1
            for block in range(1 << level - 2):
                if tables is None:
                    rotation2 = rotation * rotation % mod
                    rotation3 = rotation2 * rotation % mod
                else:
                    rotation = first[block]
                    rotation2 = second[block]
                    rotation3 = third[block]
                offset = (block << height - level + 2) * stride
                for position in range(count):
                    index = position + (position & mask)
                    value0 = values[offset + index]
                    value1 = values[offset + index + width]
                    value2 = values[offset + index + 2 * width]
                    value3 = values[offset + index + 3 * width]
                    difference = (value2 - value3) * inverse_imag % mod
                    values[offset + index] = (value0 + value1 + value2 + value3) % mod
                    values[offset + index + width] = (value0 - value1 + difference) * rotation % mod
                    values[offset + index + 2 * width] = (value0 + value1 - value2 - value3) * rotation2 % mod
                    values[offset + index + 3 * width] = (value0 - value1 - difference) * rotation3 % mod
                if tables is None:
                    rotation = rotation * irate3[(~block & -~block).bit_length()] % mod
            level -= 2
    return values

def ntt(values):
    """`values`を破壊的に順変換し、同じlistを返す。O(N log N)。"""
    return _convolution_ntt998_butterfly(values)

def _convolution_ntt998__intt(values):
    size = len(values)
    _convolution_ntt998_butterfly_inv(values)
    inverse_size = _convolution_ntt998_INVERSE_SIZE.get(size)
    if inverse_size is None:
        inverse_size = pow(size, MOD - 2, MOD)
        _convolution_ntt998_INVERSE_SIZE[size] = inverse_size
    for index in range(size):
        values[index] = values[index] * inverse_size % MOD
    return values

def intt(values):
    """`values`を破壊的に正規化済み逆変換し、同じlistを返す。O(N log N)。"""
    return _convolution_ntt998__intt(values)

def _convolution_ntt998_multiply_naive(first, second):
    first_size = len(first)
    second_size = len(second)
    if first_size == 0 or second_size == 0:
        return []
    if first_size < second_size:
        (first, second) = (second, first)
        (first_size, second_size) = (second_size, first_size)
    result = [0] * (first_size + second_size - 1)
    mod = MOD
    for (index, left) in enumerate(first):
        left %= mod
        if left:
            for (offset, right) in enumerate(second):
                result[index + offset] += left * right
        if index & 7 == 7:
            start = index
            stop = min(index + second_size, len(result))
            for position in range(start, stop):
                result[position] %= mod
    return [value % mod for value in result]

def _convolution_ntt998_multiply_without_boundary(first, second):
    if min(len(first), len(second)) <= 60:
        return _convolution_ntt998_multiply_naive(first, second)
    first_size = len(first)
    second_size = len(second)
    output_size = first_size + second_size - 1
    size = 1 << (output_size - 1).bit_length()
    _convolution_ntt998_check_length(size)
    left = [value % MOD for value in first]
    left.extend([0] * (size - first_size))
    _convolution_ntt998_butterfly(left)
    if first is second:
        for index in range(size):
            left[index] = left[index] * left[index] % MOD
    else:
        right = [value % MOD for value in second]
        right.extend([0] * (size - second_size))
        _convolution_ntt998_butterfly(right)
        for index in range(size):
            left[index] = left[index] * right[index] % MOD
    _convolution_ntt998_butterfly_inv(left)
    inverse_size = _convolution_ntt998_INVERSE_SIZE.get(size)
    if inverse_size is None:
        inverse_size = pow(size, MOD - 2, MOD)
        _convolution_ntt998_INVERSE_SIZE[size] = inverse_size
    for index in range(output_size):
        left[index] = left[index] * inverse_size % MOD
    del left[output_size:]
    return left

def multiply(first, second):
    """2つの係数列の積を長さ`len(first)+len(second)-1`で返す。O(N log N)。"""
    first_size = len(first)
    second_size = len(second)
    if first_size == 0 or second_size == 0:
        return []
    if min(first_size, second_size) <= 60:
        return _convolution_ntt998_multiply_naive(first, second)
    if first_size < second_size:
        (first, second) = (second, first)
        (first_size, second_size) = (second_size, first_size)
    output_size = first_size + second_size - 1
    lower_power = 1 << output_size.bit_length() - 1
    boundary_excess = output_size - lower_power
    if 0 < boundary_excess <= 128 and (boundary_excess * second_size <= 2 * lower_power or lower_power == 1 << 23):
        prefix = _convolution_ntt998_multiply_without_boundary(first[:-boundary_excess], second)
        prefix.extend([0] * boundary_excess)
        tail_start = first_size - boundary_excess
        for index in range(tail_start, first_size):
            left = first[index] % MOD
            if left:
                for (offset, right) in enumerate(second):
                    prefix[index + offset] += left * right
        for index in range(tail_start, output_size):
            prefix[index] %= MOD
        return prefix
    return _convolution_ntt998_multiply_without_boundary(first, second)

def square(series):
    """係数列の二乗を長さ`2*len(series)-1`で返す。O(N log N)。"""
    size = len(series)
    if size == 0:
        return []
    if size <= 60:
        result = [0] * (2 * size - 1)
        for (index, left) in enumerate(series):
            left %= MOD
            result[index << 1] += left * left
            for offset in range(index + 1, size):
                result[index + offset] += 2 * left * series[offset]
        return [value % MOD for value in result]
    return multiply(series, series)
'出力が2^23項を超える係数列も、998244353で畳み込む。\n\n各入力を分割して順NTTを再利用し、同じ出力位置へ寄与する積を\n周波数表現でまとめてから逆変換する。通常サイズはNTT998を使う。\n'
from array import array as _convolution_large_convolution_array

def _convolution_large_convolution_append_block(result, work, start, output_size, inverse_size):
    overlap = len(result) - start
    for k in range(overlap):
        value = result[start + k] + work[k] * inverse_size % MOD
        result[start + k] = value - MOD if value >= MOD else value
    for k in range(overlap, min(len(work) - 1, output_size - start)):
        result.append(work[k] * inverse_size % MOD)

def _convolution_large_convolution_multiply_short_blocks(first, second, block):
    size = block << 1
    output_size = len(first) + len(second) - 1
    inverse_size = pow(size, MOD - 2, MOD)
    fixed = [value % MOD for value in first]
    fixed.extend([0] * (size - len(fixed)))
    _convolution_ntt998_butterfly(fixed)
    result = []
    for start in range(0, len(second), block):
        work = [value % MOD for value in second[start:start + block]]
        work.extend([0] * (size - len(work)))
        _convolution_ntt998_butterfly(work)
        for k in range(size):
            work[k] = work[k] * fixed[k] % MOD
        _convolution_ntt998_butterfly_inv(work)
        _convolution_large_convolution_append_block(result, work, start, output_size, inverse_size)
    return result

def _convolution_large_convolution_multiply_blocks(first, second, block):
    if len(first) <= block < len(second):
        return _convolution_large_convolution_multiply_short_blocks(first, second, block)
    if len(second) <= block < len(first):
        return _convolution_large_convolution_multiply_short_blocks(second, first, block)
    size = block << 1
    output_size = len(first) + len(second) - 1
    same = first is second

    def transform(values):
        blocks = []
        for start in range(0, len(values), block):
            work = [value % MOD for value in values[start:start + block]]
            work.extend([0] * (size - len(work)))
            _convolution_ntt998_butterfly(work)
            blocks.append(_convolution_large_convolution_array('I', work))
        return blocks
    left = transform(first)
    right = left if same else transform(second)
    result = []
    inverse_size = pow(size, MOD - 2, MOD)
    work = [0] * size
    for diagonal in range(len(left) + len(right) - 1):
        begin = max(0, diagonal - len(right) + 1)
        end = min(len(left) - 1, diagonal)
        if same:
            end = min(end, diagonal // 2)
        for i in range(begin, end + 1):
            a = left[i]
            b = right[diagonal - i]
            if i == begin:
                scale = 2 if same and i != diagonal - i else 1
                for k in range(size):
                    work[k] = scale * a[k] * b[k] % MOD
            elif same and i != diagonal - i:
                for k in range(size):
                    work[k] = (work[k] + 2 * a[k] * b[k]) % MOD
            else:
                for k in range(size):
                    work[k] = (work[k] + a[k] * b[k]) % MOD
        _convolution_ntt998_butterfly_inv(work)
        start = diagonal * block
        _convolution_large_convolution_append_block(result, work, start, output_size, inverse_size)
        expired = diagonal - len(right) + 1
        if expired >= 0:
            left[expired] = None
        expired = diagonal - len(left) + 1
        if expired >= 0 and (not same):
            right[expired] = None
    return result

def _convolution_large_convolution_multiply_sixteen_lanes(first, second, size):
    count = len(first) + len(second) - 1
    inverse = pow(size, MOD - 2, MOD)
    a = [0] * (32 * size)
    for i in range(len(first)):
        a[i] = first[i] % MOD
    _convolution_ntt998_butterfly(a, stride=32)
    if first is second:
        b = a
    else:
        b = [0] * (32 * size)
        for i in range(len(second)):
            b[i] = second[i] * inverse % MOD
        _convolution_ntt998_butterfly(b, stride=32)
    root = pow(3, (MOD - 1) // size, MOD)
    rates = [pow(root, (size >> j + 1) - (size - (size >> j)), MOD) for j in range(size.bit_length())]
    weight = 1
    for i in range(size):
        pos = i << 5
        x0, y0 = a[pos + 0], b[pos + 0]
        x1, y1 = a[pos + 1], b[pos + 1]
        x2, y2 = a[pos + 2], b[pos + 2]
        x3, y3 = a[pos + 3], b[pos + 3]
        x4, y4 = a[pos + 4], b[pos + 4]
        x5, y5 = a[pos + 5], b[pos + 5]
        x6, y6 = a[pos + 6], b[pos + 6]
        x7, y7 = a[pos + 7], b[pos + 7]
        x8, y8 = a[pos + 8], b[pos + 8]
        x9, y9 = a[pos + 9], b[pos + 9]
        x10, y10 = a[pos + 10], b[pos + 10]
        x11, y11 = a[pos + 11], b[pos + 11]
        x12, y12 = a[pos + 12], b[pos + 12]
        x13, y13 = a[pos + 13], b[pos + 13]
        x14, y14 = a[pos + 14], b[pos + 14]
        x15, y15 = a[pos + 15], b[pos + 15]
        x16, y16 = a[pos + 16], b[pos + 16]
        x17, y17 = a[pos + 17], b[pos + 17]
        x18, y18 = a[pos + 18], b[pos + 18]
        x19, y19 = a[pos + 19], b[pos + 19]
        x20, y20 = a[pos + 20], b[pos + 20]
        x21, y21 = a[pos + 21], b[pos + 21]
        x22, y22 = a[pos + 22], b[pos + 22]
        x23, y23 = a[pos + 23], b[pos + 23]
        x24, y24 = a[pos + 24], b[pos + 24]
        x25, y25 = a[pos + 25], b[pos + 25]
        x26, y26 = a[pos + 26], b[pos + 26]
        x27, y27 = a[pos + 27], b[pos + 27]
        x28, y28 = a[pos + 28], b[pos + 28]
        x29, y29 = a[pos + 29], b[pos + 29]
        x30, y30 = a[pos + 30], b[pos + 30]
        x31, y31 = a[pos + 31], b[pos + 31]
        c0 = (x0 * y0) % MOD
        c1 = (x0 * y1 + x1 * y0) % MOD
        c2 = (x0 * y2 + x1 * y1 + x2 * y0) % MOD
        c3 = (x0 * y3 + x1 * y2 + x2 * y1 + x3 * y0) % MOD
        c4 = (x0 * y4 + x1 * y3 + x2 * y2 + x3 * y1 + x4 * y0) % MOD
        c5 = (x0 * y5 + x1 * y4 + x2 * y3 + x3 * y2 + x4 * y1 + x5 * y0) % MOD
        c6 = (x0 * y6 + x1 * y5 + x2 * y4 + x3 * y3 + x4 * y2 + x5 * y1 + x6 * y0) % MOD
        c7 = (x0 * y7 + x1 * y6 + x2 * y5 + x3 * y4 + x4 * y3 + x5 * y2 + x6 * y1 + x7 * y0) % MOD
        c8 = (x0 * y8 + x1 * y7 + x2 * y6 + x3 * y5 + x4 * y4 + x5 * y3 + x6 * y2 + x7 * y1) % MOD + (x8 * y0) % MOD
        c9 = (x0 * y9 + x1 * y8 + x2 * y7 + x3 * y6 + x4 * y5 + x5 * y4 + x6 * y3 + x7 * y2) % MOD + (x8 * y1 + x9 * y0) % MOD
        c10 = (x0 * y10 + x1 * y9 + x2 * y8 + x3 * y7 + x4 * y6 + x5 * y5 + x6 * y4 + x7 * y3) % MOD + (x8 * y2 + x9 * y1 + x10 * y0) % MOD
        c11 = (x0 * y11 + x1 * y10 + x2 * y9 + x3 * y8 + x4 * y7 + x5 * y6 + x6 * y5 + x7 * y4) % MOD + (x8 * y3 + x9 * y2 + x10 * y1 + x11 * y0) % MOD
        c12 = (x0 * y12 + x1 * y11 + x2 * y10 + x3 * y9 + x4 * y8 + x5 * y7 + x6 * y6 + x7 * y5) % MOD + (x8 * y4 + x9 * y3 + x10 * y2 + x11 * y1 + x12 * y0) % MOD
        c13 = (x0 * y13 + x1 * y12 + x2 * y11 + x3 * y10 + x4 * y9 + x5 * y8 + x6 * y7 + x7 * y6) % MOD + (x8 * y5 + x9 * y4 + x10 * y3 + x11 * y2 + x12 * y1 + x13 * y0) % MOD
        c14 = (x0 * y14 + x1 * y13 + x2 * y12 + x3 * y11 + x4 * y10 + x5 * y9 + x6 * y8 + x7 * y7) % MOD + (x8 * y6 + x9 * y5 + x10 * y4 + x11 * y3 + x12 * y2 + x13 * y1 + x14 * y0) % MOD
        c15 = (x0 * y15 + x1 * y14 + x2 * y13 + x3 * y12 + x4 * y11 + x5 * y10 + x6 * y9 + x7 * y8) % MOD + (x8 * y7 + x9 * y6 + x10 * y5 + x11 * y4 + x12 * y3 + x13 * y2 + x14 * y1 + x15 * y0) % MOD
        c16 = (x0 * y16 + x1 * y15 + x2 * y14 + x3 * y13 + x4 * y12 + x5 * y11 + x6 * y10 + x7 * y9) % MOD + (x8 * y8 + x9 * y7 + x10 * y6 + x11 * y5 + x12 * y4 + x13 * y3 + x14 * y2 + x15 * y1) % MOD + (x16 * y0) % MOD
        c17 = (x0 * y17 + x1 * y16 + x2 * y15 + x3 * y14 + x4 * y13 + x5 * y12 + x6 * y11 + x7 * y10) % MOD + (x8 * y9 + x9 * y8 + x10 * y7 + x11 * y6 + x12 * y5 + x13 * y4 + x14 * y3 + x15 * y2) % MOD + (x16 * y1 + x17 * y0) % MOD
        c18 = (x0 * y18 + x1 * y17 + x2 * y16 + x3 * y15 + x4 * y14 + x5 * y13 + x6 * y12 + x7 * y11) % MOD + (x8 * y10 + x9 * y9 + x10 * y8 + x11 * y7 + x12 * y6 + x13 * y5 + x14 * y4 + x15 * y3) % MOD + (x16 * y2 + x17 * y1 + x18 * y0) % MOD
        c19 = (x0 * y19 + x1 * y18 + x2 * y17 + x3 * y16 + x4 * y15 + x5 * y14 + x6 * y13 + x7 * y12) % MOD + (x8 * y11 + x9 * y10 + x10 * y9 + x11 * y8 + x12 * y7 + x13 * y6 + x14 * y5 + x15 * y4) % MOD + (x16 * y3 + x17 * y2 + x18 * y1 + x19 * y0) % MOD
        c20 = (x0 * y20 + x1 * y19 + x2 * y18 + x3 * y17 + x4 * y16 + x5 * y15 + x6 * y14 + x7 * y13) % MOD + (x8 * y12 + x9 * y11 + x10 * y10 + x11 * y9 + x12 * y8 + x13 * y7 + x14 * y6 + x15 * y5) % MOD + (x16 * y4 + x17 * y3 + x18 * y2 + x19 * y1 + x20 * y0) % MOD
        c21 = (x0 * y21 + x1 * y20 + x2 * y19 + x3 * y18 + x4 * y17 + x5 * y16 + x6 * y15 + x7 * y14) % MOD + (x8 * y13 + x9 * y12 + x10 * y11 + x11 * y10 + x12 * y9 + x13 * y8 + x14 * y7 + x15 * y6) % MOD + (x16 * y5 + x17 * y4 + x18 * y3 + x19 * y2 + x20 * y1 + x21 * y0) % MOD
        c22 = (x0 * y22 + x1 * y21 + x2 * y20 + x3 * y19 + x4 * y18 + x5 * y17 + x6 * y16 + x7 * y15) % MOD + (x8 * y14 + x9 * y13 + x10 * y12 + x11 * y11 + x12 * y10 + x13 * y9 + x14 * y8 + x15 * y7) % MOD + (x16 * y6 + x17 * y5 + x18 * y4 + x19 * y3 + x20 * y2 + x21 * y1 + x22 * y0) % MOD
        c23 = (x0 * y23 + x1 * y22 + x2 * y21 + x3 * y20 + x4 * y19 + x5 * y18 + x6 * y17 + x7 * y16) % MOD + (x8 * y15 + x9 * y14 + x10 * y13 + x11 * y12 + x12 * y11 + x13 * y10 + x14 * y9 + x15 * y8) % MOD + (x16 * y7 + x17 * y6 + x18 * y5 + x19 * y4 + x20 * y3 + x21 * y2 + x22 * y1 + x23 * y0) % MOD
        c24 = (x0 * y24 + x1 * y23 + x2 * y22 + x3 * y21 + x4 * y20 + x5 * y19 + x6 * y18 + x7 * y17) % MOD + (x8 * y16 + x9 * y15 + x10 * y14 + x11 * y13 + x12 * y12 + x13 * y11 + x14 * y10 + x15 * y9) % MOD + (x16 * y8 + x17 * y7 + x18 * y6 + x19 * y5 + x20 * y4 + x21 * y3 + x22 * y2 + x23 * y1) % MOD + (x24 * y0) % MOD
        c25 = (x0 * y25 + x1 * y24 + x2 * y23 + x3 * y22 + x4 * y21 + x5 * y20 + x6 * y19 + x7 * y18) % MOD + (x8 * y17 + x9 * y16 + x10 * y15 + x11 * y14 + x12 * y13 + x13 * y12 + x14 * y11 + x15 * y10) % MOD + (x16 * y9 + x17 * y8 + x18 * y7 + x19 * y6 + x20 * y5 + x21 * y4 + x22 * y3 + x23 * y2) % MOD + (x24 * y1 + x25 * y0) % MOD
        c26 = (x0 * y26 + x1 * y25 + x2 * y24 + x3 * y23 + x4 * y22 + x5 * y21 + x6 * y20 + x7 * y19) % MOD + (x8 * y18 + x9 * y17 + x10 * y16 + x11 * y15 + x12 * y14 + x13 * y13 + x14 * y12 + x15 * y11) % MOD + (x16 * y10 + x17 * y9 + x18 * y8 + x19 * y7 + x20 * y6 + x21 * y5 + x22 * y4 + x23 * y3) % MOD + (x24 * y2 + x25 * y1 + x26 * y0) % MOD
        c27 = (x0 * y27 + x1 * y26 + x2 * y25 + x3 * y24 + x4 * y23 + x5 * y22 + x6 * y21 + x7 * y20) % MOD + (x8 * y19 + x9 * y18 + x10 * y17 + x11 * y16 + x12 * y15 + x13 * y14 + x14 * y13 + x15 * y12) % MOD + (x16 * y11 + x17 * y10 + x18 * y9 + x19 * y8 + x20 * y7 + x21 * y6 + x22 * y5 + x23 * y4) % MOD + (x24 * y3 + x25 * y2 + x26 * y1 + x27 * y0) % MOD
        c28 = (x0 * y28 + x1 * y27 + x2 * y26 + x3 * y25 + x4 * y24 + x5 * y23 + x6 * y22 + x7 * y21) % MOD + (x8 * y20 + x9 * y19 + x10 * y18 + x11 * y17 + x12 * y16 + x13 * y15 + x14 * y14 + x15 * y13) % MOD + (x16 * y12 + x17 * y11 + x18 * y10 + x19 * y9 + x20 * y8 + x21 * y7 + x22 * y6 + x23 * y5) % MOD + (x24 * y4 + x25 * y3 + x26 * y2 + x27 * y1 + x28 * y0) % MOD
        c29 = (x0 * y29 + x1 * y28 + x2 * y27 + x3 * y26 + x4 * y25 + x5 * y24 + x6 * y23 + x7 * y22) % MOD + (x8 * y21 + x9 * y20 + x10 * y19 + x11 * y18 + x12 * y17 + x13 * y16 + x14 * y15 + x15 * y14) % MOD + (x16 * y13 + x17 * y12 + x18 * y11 + x19 * y10 + x20 * y9 + x21 * y8 + x22 * y7 + x23 * y6) % MOD + (x24 * y5 + x25 * y4 + x26 * y3 + x27 * y2 + x28 * y1 + x29 * y0) % MOD
        c30 = (x0 * y30 + x1 * y29 + x2 * y28 + x3 * y27 + x4 * y26 + x5 * y25 + x6 * y24 + x7 * y23) % MOD + (x8 * y22 + x9 * y21 + x10 * y20 + x11 * y19 + x12 * y18 + x13 * y17 + x14 * y16 + x15 * y15) % MOD + (x16 * y14 + x17 * y13 + x18 * y12 + x19 * y11 + x20 * y10 + x21 * y9 + x22 * y8 + x23 * y7) % MOD + (x24 * y6 + x25 * y5 + x26 * y4 + x27 * y3 + x28 * y2 + x29 * y1 + x30 * y0) % MOD
        c31 = (x0 * y31 + x1 * y30 + x2 * y29 + x3 * y28 + x4 * y27 + x5 * y26 + x6 * y25 + x7 * y24) % MOD + (x8 * y23 + x9 * y22 + x10 * y21 + x11 * y20 + x12 * y19 + x13 * y18 + x14 * y17 + x15 * y16) % MOD + (x16 * y15 + x17 * y14 + x18 * y13 + x19 * y12 + x20 * y11 + x21 * y10 + x22 * y9 + x23 * y8) % MOD + (x24 * y7 + x25 * y6 + x26 * y5 + x27 * y4 + x28 * y3 + x29 * y2 + x30 * y1 + x31 * y0) % MOD
        c32 = (x1 * y31 + x2 * y30 + x3 * y29 + x4 * y28 + x5 * y27 + x6 * y26 + x7 * y25 + x8 * y24) % MOD + (x9 * y23 + x10 * y22 + x11 * y21 + x12 * y20 + x13 * y19 + x14 * y18 + x15 * y17 + x16 * y16) % MOD + (x17 * y15 + x18 * y14 + x19 * y13 + x20 * y12 + x21 * y11 + x22 * y10 + x23 * y9 + x24 * y8) % MOD + (x25 * y7 + x26 * y6 + x27 * y5 + x28 * y4 + x29 * y3 + x30 * y2 + x31 * y1) % MOD
        c33 = (x2 * y31 + x3 * y30 + x4 * y29 + x5 * y28 + x6 * y27 + x7 * y26 + x8 * y25 + x9 * y24) % MOD + (x10 * y23 + x11 * y22 + x12 * y21 + x13 * y20 + x14 * y19 + x15 * y18 + x16 * y17 + x17 * y16) % MOD + (x18 * y15 + x19 * y14 + x20 * y13 + x21 * y12 + x22 * y11 + x23 * y10 + x24 * y9 + x25 * y8) % MOD + (x26 * y7 + x27 * y6 + x28 * y5 + x29 * y4 + x30 * y3 + x31 * y2) % MOD
        c34 = (x3 * y31 + x4 * y30 + x5 * y29 + x6 * y28 + x7 * y27 + x8 * y26 + x9 * y25 + x10 * y24) % MOD + (x11 * y23 + x12 * y22 + x13 * y21 + x14 * y20 + x15 * y19 + x16 * y18 + x17 * y17 + x18 * y16) % MOD + (x19 * y15 + x20 * y14 + x21 * y13 + x22 * y12 + x23 * y11 + x24 * y10 + x25 * y9 + x26 * y8) % MOD + (x27 * y7 + x28 * y6 + x29 * y5 + x30 * y4 + x31 * y3) % MOD
        c35 = (x4 * y31 + x5 * y30 + x6 * y29 + x7 * y28 + x8 * y27 + x9 * y26 + x10 * y25 + x11 * y24) % MOD + (x12 * y23 + x13 * y22 + x14 * y21 + x15 * y20 + x16 * y19 + x17 * y18 + x18 * y17 + x19 * y16) % MOD + (x20 * y15 + x21 * y14 + x22 * y13 + x23 * y12 + x24 * y11 + x25 * y10 + x26 * y9 + x27 * y8) % MOD + (x28 * y7 + x29 * y6 + x30 * y5 + x31 * y4) % MOD
        c36 = (x5 * y31 + x6 * y30 + x7 * y29 + x8 * y28 + x9 * y27 + x10 * y26 + x11 * y25 + x12 * y24) % MOD + (x13 * y23 + x14 * y22 + x15 * y21 + x16 * y20 + x17 * y19 + x18 * y18 + x19 * y17 + x20 * y16) % MOD + (x21 * y15 + x22 * y14 + x23 * y13 + x24 * y12 + x25 * y11 + x26 * y10 + x27 * y9 + x28 * y8) % MOD + (x29 * y7 + x30 * y6 + x31 * y5) % MOD
        c37 = (x6 * y31 + x7 * y30 + x8 * y29 + x9 * y28 + x10 * y27 + x11 * y26 + x12 * y25 + x13 * y24) % MOD + (x14 * y23 + x15 * y22 + x16 * y21 + x17 * y20 + x18 * y19 + x19 * y18 + x20 * y17 + x21 * y16) % MOD + (x22 * y15 + x23 * y14 + x24 * y13 + x25 * y12 + x26 * y11 + x27 * y10 + x28 * y9 + x29 * y8) % MOD + (x30 * y7 + x31 * y6) % MOD
        c38 = (x7 * y31 + x8 * y30 + x9 * y29 + x10 * y28 + x11 * y27 + x12 * y26 + x13 * y25 + x14 * y24) % MOD + (x15 * y23 + x16 * y22 + x17 * y21 + x18 * y20 + x19 * y19 + x20 * y18 + x21 * y17 + x22 * y16) % MOD + (x23 * y15 + x24 * y14 + x25 * y13 + x26 * y12 + x27 * y11 + x28 * y10 + x29 * y9 + x30 * y8) % MOD + (x31 * y7) % MOD
        c39 = (x8 * y31 + x9 * y30 + x10 * y29 + x11 * y28 + x12 * y27 + x13 * y26 + x14 * y25 + x15 * y24) % MOD + (x16 * y23 + x17 * y22 + x18 * y21 + x19 * y20 + x20 * y19 + x21 * y18 + x22 * y17 + x23 * y16) % MOD + (x24 * y15 + x25 * y14 + x26 * y13 + x27 * y12 + x28 * y11 + x29 * y10 + x30 * y9 + x31 * y8) % MOD
        c40 = (x9 * y31 + x10 * y30 + x11 * y29 + x12 * y28 + x13 * y27 + x14 * y26 + x15 * y25 + x16 * y24) % MOD + (x17 * y23 + x18 * y22 + x19 * y21 + x20 * y20 + x21 * y19 + x22 * y18 + x23 * y17 + x24 * y16) % MOD + (x25 * y15 + x26 * y14 + x27 * y13 + x28 * y12 + x29 * y11 + x30 * y10 + x31 * y9) % MOD
        c41 = (x10 * y31 + x11 * y30 + x12 * y29 + x13 * y28 + x14 * y27 + x15 * y26 + x16 * y25 + x17 * y24) % MOD + (x18 * y23 + x19 * y22 + x20 * y21 + x21 * y20 + x22 * y19 + x23 * y18 + x24 * y17 + x25 * y16) % MOD + (x26 * y15 + x27 * y14 + x28 * y13 + x29 * y12 + x30 * y11 + x31 * y10) % MOD
        c42 = (x11 * y31 + x12 * y30 + x13 * y29 + x14 * y28 + x15 * y27 + x16 * y26 + x17 * y25 + x18 * y24) % MOD + (x19 * y23 + x20 * y22 + x21 * y21 + x22 * y20 + x23 * y19 + x24 * y18 + x25 * y17 + x26 * y16) % MOD + (x27 * y15 + x28 * y14 + x29 * y13 + x30 * y12 + x31 * y11) % MOD
        c43 = (x12 * y31 + x13 * y30 + x14 * y29 + x15 * y28 + x16 * y27 + x17 * y26 + x18 * y25 + x19 * y24) % MOD + (x20 * y23 + x21 * y22 + x22 * y21 + x23 * y20 + x24 * y19 + x25 * y18 + x26 * y17 + x27 * y16) % MOD + (x28 * y15 + x29 * y14 + x30 * y13 + x31 * y12) % MOD
        c44 = (x13 * y31 + x14 * y30 + x15 * y29 + x16 * y28 + x17 * y27 + x18 * y26 + x19 * y25 + x20 * y24) % MOD + (x21 * y23 + x22 * y22 + x23 * y21 + x24 * y20 + x25 * y19 + x26 * y18 + x27 * y17 + x28 * y16) % MOD + (x29 * y15 + x30 * y14 + x31 * y13) % MOD
        c45 = (x14 * y31 + x15 * y30 + x16 * y29 + x17 * y28 + x18 * y27 + x19 * y26 + x20 * y25 + x21 * y24) % MOD + (x22 * y23 + x23 * y22 + x24 * y21 + x25 * y20 + x26 * y19 + x27 * y18 + x28 * y17 + x29 * y16) % MOD + (x30 * y15 + x31 * y14) % MOD
        c46 = (x15 * y31 + x16 * y30 + x17 * y29 + x18 * y28 + x19 * y27 + x20 * y26 + x21 * y25 + x22 * y24) % MOD + (x23 * y23 + x24 * y22 + x25 * y21 + x26 * y20 + x27 * y19 + x28 * y18 + x29 * y17 + x30 * y16) % MOD + (x31 * y15) % MOD
        c47 = (x16 * y31 + x17 * y30 + x18 * y29 + x19 * y28 + x20 * y27 + x21 * y26 + x22 * y25 + x23 * y24) % MOD + (x24 * y23 + x25 * y22 + x26 * y21 + x27 * y20 + x28 * y19 + x29 * y18 + x30 * y17 + x31 * y16) % MOD
        c48 = (x17 * y31 + x18 * y30 + x19 * y29 + x20 * y28 + x21 * y27 + x22 * y26 + x23 * y25 + x24 * y24) % MOD + (x25 * y23 + x26 * y22 + x27 * y21 + x28 * y20 + x29 * y19 + x30 * y18 + x31 * y17) % MOD
        c49 = (x18 * y31 + x19 * y30 + x20 * y29 + x21 * y28 + x22 * y27 + x23 * y26 + x24 * y25 + x25 * y24) % MOD + (x26 * y23 + x27 * y22 + x28 * y21 + x29 * y20 + x30 * y19 + x31 * y18) % MOD
        c50 = (x19 * y31 + x20 * y30 + x21 * y29 + x22 * y28 + x23 * y27 + x24 * y26 + x25 * y25 + x26 * y24) % MOD + (x27 * y23 + x28 * y22 + x29 * y21 + x30 * y20 + x31 * y19) % MOD
        c51 = (x20 * y31 + x21 * y30 + x22 * y29 + x23 * y28 + x24 * y27 + x25 * y26 + x26 * y25 + x27 * y24) % MOD + (x28 * y23 + x29 * y22 + x30 * y21 + x31 * y20) % MOD
        c52 = (x21 * y31 + x22 * y30 + x23 * y29 + x24 * y28 + x25 * y27 + x26 * y26 + x27 * y25 + x28 * y24) % MOD + (x29 * y23 + x30 * y22 + x31 * y21) % MOD
        c53 = (x22 * y31 + x23 * y30 + x24 * y29 + x25 * y28 + x26 * y27 + x27 * y26 + x28 * y25 + x29 * y24) % MOD + (x30 * y23 + x31 * y22) % MOD
        c54 = (x23 * y31 + x24 * y30 + x25 * y29 + x26 * y28 + x27 * y27 + x28 * y26 + x29 * y25 + x30 * y24) % MOD + (x31 * y23) % MOD
        c55 = (x24 * y31 + x25 * y30 + x26 * y29 + x27 * y28 + x28 * y27 + x29 * y26 + x30 * y25 + x31 * y24) % MOD
        c56 = (x25 * y31 + x26 * y30 + x27 * y29 + x28 * y28 + x29 * y27 + x30 * y26 + x31 * y25) % MOD
        c57 = (x26 * y31 + x27 * y30 + x28 * y29 + x29 * y28 + x30 * y27 + x31 * y26) % MOD
        c58 = (x27 * y31 + x28 * y30 + x29 * y29 + x30 * y28 + x31 * y27) % MOD
        c59 = (x28 * y31 + x29 * y30 + x30 * y29 + x31 * y28) % MOD
        c60 = (x29 * y31 + x30 * y30 + x31 * y29) % MOD
        c61 = (x30 * y31 + x31 * y30) % MOD
        c62 = (x31 * y31) % MOD
        a[pos + 0] = (c0 + weight * (c32 % MOD)) % MOD
        a[pos + 1] = (c1 + weight * (c33 % MOD)) % MOD
        a[pos + 2] = (c2 + weight * (c34 % MOD)) % MOD
        a[pos + 3] = (c3 + weight * (c35 % MOD)) % MOD
        a[pos + 4] = (c4 + weight * (c36 % MOD)) % MOD
        a[pos + 5] = (c5 + weight * (c37 % MOD)) % MOD
        a[pos + 6] = (c6 + weight * (c38 % MOD)) % MOD
        a[pos + 7] = (c7 + weight * (c39 % MOD)) % MOD
        a[pos + 8] = (c8 + weight * (c40 % MOD)) % MOD
        a[pos + 9] = (c9 + weight * (c41 % MOD)) % MOD
        a[pos + 10] = (c10 + weight * (c42 % MOD)) % MOD
        a[pos + 11] = (c11 + weight * (c43 % MOD)) % MOD
        a[pos + 12] = (c12 + weight * (c44 % MOD)) % MOD
        a[pos + 13] = (c13 + weight * (c45 % MOD)) % MOD
        a[pos + 14] = (c14 + weight * (c46 % MOD)) % MOD
        a[pos + 15] = (c15 + weight * (c47 % MOD)) % MOD
        a[pos + 16] = (c16 + weight * (c48 % MOD)) % MOD
        a[pos + 17] = (c17 + weight * (c49 % MOD)) % MOD
        a[pos + 18] = (c18 + weight * (c50 % MOD)) % MOD
        a[pos + 19] = (c19 + weight * (c51 % MOD)) % MOD
        a[pos + 20] = (c20 + weight * (c52 % MOD)) % MOD
        a[pos + 21] = (c21 + weight * (c53 % MOD)) % MOD
        a[pos + 22] = (c22 + weight * (c54 % MOD)) % MOD
        a[pos + 23] = (c23 + weight * (c55 % MOD)) % MOD
        a[pos + 24] = (c24 + weight * (c56 % MOD)) % MOD
        a[pos + 25] = (c25 + weight * (c57 % MOD)) % MOD
        a[pos + 26] = (c26 + weight * (c58 % MOD)) % MOD
        a[pos + 27] = (c27 + weight * (c59 % MOD)) % MOD
        a[pos + 28] = (c28 + weight * (c60 % MOD)) % MOD
        a[pos + 29] = (c29 + weight * (c61 % MOD)) % MOD
        a[pos + 30] = (c30 + weight * (c62 % MOD)) % MOD
        a[pos + 31] = c31 % MOD
        weight = weight * rates[(i + 1 & -(i + 1)).bit_length() - 1] % MOD
    del b
    _convolution_ntt998_butterfly_inv(a, stride=32)
    if first is second:
        for i in range(count):
            a[i] = a[i] * inverse % MOD
    del a[count:]
    return a

def _convolution_large_convolution_multiply(first, second):
    """昇べき係数列の積をmod 998244353で返す。入力は変更しない。"""
    if not first or not second:
        return []
    shorter = min(len(first), len(second))
    if len(first) + len(second) - 1 <= 1 << 23 or shorter <= 60:
        return multiply(first, second)
    if (len(first) + len(second) - 2).bit_length() == 25:
        blocks = (len(first) + (1 << 22) - 1) // (1 << 22)
        blocks += (len(second) + (1 << 22) - 1) // (1 << 22)
        if blocks >= 7:
            return _convolution_large_convolution_multiply_sixteen_lanes(first, second, 1 << 20)
    block = min(1 << 22, 1 << (shorter - 1).bit_length())
    return _convolution_large_convolution_multiply_blocks(first, second, block)
import sys
from array import array

def read_coefficients(stream, n):
    result = array('I')
    carry = b''
    while len(result) < n:
        chunk = stream.read(1 << 16)
        if not chunk:
            result.extend(map(int, carry.split()))
            break
        chunk = carry + chunk
        end = len(chunk)
        while end and chunk[end - 1] > 32:
            end -= 1
        result.extend(map(int, chunk[:end].split()))
        carry = chunk[end:]
    if len(result) != n:
        raise ValueError('unexpected number of coefficients')
    return result

def main():
    stream = sys.stdin.buffer
    (n, m) = map(int, stream.readline().split())
    values = read_coefficients(stream, n + m)
    first = values[:n]
    del values[:n]
    result = _convolution_large_convolution_multiply(first, values)
    for start in range(0, len(result), 8192):
        if start:
            sys.stdout.write(' ')
        sys.stdout.write(' '.join(map(str, result[start:start + 8192])))
    sys.stdout.write('\n')
if __name__ == '__main__':
    main()
