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

def _convolution_large_convolution_multiply_four_lanes(first, second, size):
    count = len(first) + len(second) - 1
    inverse = pow(size, MOD - 2, MOD)
    a = [0] * (16 * size)
    for i in range(len(first)):
        a[i] = first[i] % MOD
    _convolution_ntt998_butterfly(a, stride=16)
    if first is second:
        b = a
    else:
        b = [0] * (16 * size)
        for i in range(len(second)):
            b[i] = second[i] * inverse % MOD
        _convolution_ntt998_butterfly(b, stride=16)
    root = pow(3, (MOD - 1) // size, MOD)
    rates = [pow(root, (size >> j + 1) - (size - (size >> j)), MOD) for j in range(size.bit_length())]
    weight = 1
    for i in range(size):
        pos = i << 4
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
        z0 = x0 - x8
        z1 = x1 - x9
        z2 = x2 - x10
        z3 = x3 - x11
        z4 = x4 - x12
        z5 = x5 - x13
        z6 = x6 - x14
        z7 = x7 - x15
        z8 = y0 - y8
        z9 = y1 - y9
        z10 = y2 - y10
        z11 = y3 - y11
        z12 = y4 - y12
        z13 = y5 - y13
        z14 = y6 - y14
        z15 = y7 - y15
        z16 = x0 - x4
        z17 = x1 - x5
        z18 = x2 - x6
        z19 = x3 - x7
        z20 = y0 - y4
        z21 = y1 - y5
        z22 = y2 - y6
        z23 = y3 - y7
        z24 = x0 * y0
        z25 = x0 * y1 + x1 * y0
        z26 = x0 * y2 + x1 * y1 + x2 * y0
        z27 = x0 * y3 + x1 * y2 + x2 * y1 + x3 * y0
        z28 = x1 * y3 + x2 * y2 + x3 * y1
        z29 = x2 * y3 + x3 * y2
        z30 = x3 * y3
        z31 = x4 * y4
        z32 = x4 * y5 + x5 * y4
        z33 = x4 * y6 + x5 * y5 + x6 * y4
        z34 = x4 * y7 + x5 * y6 + x6 * y5 + x7 * y4
        z35 = x5 * y7 + x6 * y6 + x7 * y5
        z36 = x6 * y7 + x7 * y6
        z37 = x7 * y7
        z38 = z16 * z20
        z39 = z16 * z21 + z17 * z20
        z40 = z16 * z22 + z17 * z21 + z18 * z20
        z41 = z16 * z23 + z17 * z22 + z18 * z21 + z19 * z20
        z42 = z17 * z23 + z18 * z22 + z19 * z21
        z43 = z18 * z23 + z19 * z22
        z44 = z19 * z23
        z45 = z24 + z31 - z38
        z46 = z25 + z32 - z39
        z47 = z26 + z33 - z40
        z48 = z27 + z34 - z41
        z49 = z28 + z35 - z42
        z50 = z29 + z36 - z43
        z51 = z30 + z37 - z44
        z52 = z24
        z53 = z25
        z54 = z26
        z55 = z27
        z56 = z28 + z45
        z57 = z29 + z46
        z58 = z30 + z47
        z59 = z48
        z60 = z49 + z31
        z61 = z50 + z32
        z62 = z51 + z33
        z63 = z34
        z64 = z35
        z65 = z36
        z66 = z37
        z67 = x8 - x12
        z68 = x9 - x13
        z69 = x10 - x14
        z70 = x11 - x15
        z71 = y8 - y12
        z72 = y9 - y13
        z73 = y10 - y14
        z74 = y11 - y15
        z75 = x8 * y8
        z76 = x8 * y9 + x9 * y8
        z77 = x8 * y10 + x9 * y9 + x10 * y8
        z78 = x8 * y11 + x9 * y10 + x10 * y9 + x11 * y8
        z79 = x9 * y11 + x10 * y10 + x11 * y9
        z80 = x10 * y11 + x11 * y10
        z81 = x11 * y11
        z82 = x12 * y12
        z83 = x12 * y13 + x13 * y12
        z84 = x12 * y14 + x13 * y13 + x14 * y12
        z85 = x12 * y15 + x13 * y14 + x14 * y13 + x15 * y12
        z86 = x13 * y15 + x14 * y14 + x15 * y13
        z87 = x14 * y15 + x15 * y14
        z88 = x15 * y15
        z89 = z67 * z71
        z90 = z67 * z72 + z68 * z71
        z91 = z67 * z73 + z68 * z72 + z69 * z71
        z92 = z67 * z74 + z68 * z73 + z69 * z72 + z70 * z71
        z93 = z68 * z74 + z69 * z73 + z70 * z72
        z94 = z69 * z74 + z70 * z73
        z95 = z70 * z74
        z96 = z75 + z82 - z89
        z97 = z76 + z83 - z90
        z98 = z77 + z84 - z91
        z99 = z78 + z85 - z92
        z100 = z79 + z86 - z93
        z101 = z80 + z87 - z94
        z102 = z81 + z88 - z95
        z103 = z75
        z104 = z76
        z105 = z77
        z106 = z78
        z107 = z79 + z96
        z108 = z80 + z97
        z109 = z81 + z98
        z110 = z99
        z111 = z100 + z82
        z112 = z101 + z83
        z113 = z102 + z84
        z114 = z85
        z115 = z86
        z116 = z87
        z117 = z88
        z118 = z0 - z4
        z119 = z1 - z5
        z120 = z2 - z6
        z121 = z3 - z7
        z122 = z8 - z12
        z123 = z9 - z13
        z124 = z10 - z14
        z125 = z11 - z15
        z126 = z0 * z8
        z127 = z0 * z9 + z1 * z8
        z128 = z0 * z10 + z1 * z9 + z2 * z8
        z129 = z0 * z11 + z1 * z10 + z2 * z9 + z3 * z8
        z130 = z1 * z11 + z2 * z10 + z3 * z9
        z131 = z2 * z11 + z3 * z10
        z132 = z3 * z11
        z133 = z4 * z12
        z134 = z4 * z13 + z5 * z12
        z135 = z4 * z14 + z5 * z13 + z6 * z12
        z136 = z4 * z15 + z5 * z14 + z6 * z13 + z7 * z12
        z137 = z5 * z15 + z6 * z14 + z7 * z13
        z138 = z6 * z15 + z7 * z14
        z139 = z7 * z15
        z140 = z118 * z122
        z141 = z118 * z123 + z119 * z122
        z142 = z118 * z124 + z119 * z123 + z120 * z122
        z143 = z118 * z125 + z119 * z124 + z120 * z123 + z121 * z122
        z144 = z119 * z125 + z120 * z124 + z121 * z123
        z145 = z120 * z125 + z121 * z124
        z146 = z121 * z125
        z147 = z126 + z133 - z140
        z148 = z127 + z134 - z141
        z149 = z128 + z135 - z142
        z150 = z129 + z136 - z143
        z151 = z130 + z137 - z144
        z152 = z131 + z138 - z145
        z153 = z132 + z139 - z146
        z154 = z126
        z155 = z127
        z156 = z128
        z157 = z129
        z158 = z130 + z147
        z159 = z131 + z148
        z160 = z132 + z149
        z161 = z150
        z162 = z151 + z133
        z163 = z152 + z134
        z164 = z153 + z135
        z165 = z136
        z166 = z137
        z167 = z138
        z168 = z139
        z169 = z52 + z103 - z154
        z170 = z53 + z104 - z155
        z171 = z54 + z105 - z156
        z172 = z55 + z106 - z157
        z173 = z56 + z107 - z158
        z174 = z57 + z108 - z159
        z175 = z58 + z109 - z160
        z176 = z59 + z110 - z161
        z177 = z60 + z111 - z162
        z178 = z61 + z112 - z163
        z179 = z62 + z113 - z164
        z180 = z63 + z114 - z165
        z181 = z64 + z115 - z166
        z182 = z65 + z116 - z167
        z183 = z66 + z117 - z168
        z184 = z52
        z185 = z53
        z186 = z54
        z187 = z55
        z188 = z56
        z189 = z57
        z190 = z58
        z191 = z59
        z192 = z60 + z169
        z193 = z61 + z170
        z194 = z62 + z171
        z195 = z63 + z172
        z196 = z64 + z173
        z197 = z65 + z174
        z198 = z66 + z175
        z199 = z176
        z200 = z177 + z103
        z201 = z178 + z104
        z202 = z179 + z105
        z203 = z180 + z106
        z204 = z181 + z107
        z205 = z182 + z108
        z206 = z183 + z109
        z207 = z110
        z208 = z111
        z209 = z112
        z210 = z113
        z211 = z114
        z212 = z115
        z213 = z116
        z214 = z117
        a[pos + 0] = (z184 + weight * (z200 % MOD)) % MOD
        a[pos + 1] = (z185 + weight * (z201 % MOD)) % MOD
        a[pos + 2] = (z186 + weight * (z202 % MOD)) % MOD
        a[pos + 3] = (z187 + weight * (z203 % MOD)) % MOD
        a[pos + 4] = (z188 + weight * (z204 % MOD)) % MOD
        a[pos + 5] = (z189 + weight * (z205 % MOD)) % MOD
        a[pos + 6] = (z190 + weight * (z206 % MOD)) % MOD
        a[pos + 7] = (z191 + weight * (z207 % MOD)) % MOD
        a[pos + 8] = (z192 + weight * (z208 % MOD)) % MOD
        a[pos + 9] = (z193 + weight * (z209 % MOD)) % MOD
        a[pos + 10] = (z194 + weight * (z210 % MOD)) % MOD
        a[pos + 11] = (z195 + weight * (z211 % MOD)) % MOD
        a[pos + 12] = (z196 + weight * (z212 % MOD)) % MOD
        a[pos + 13] = (z197 + weight * (z213 % MOD)) % MOD
        a[pos + 14] = (z198 + weight * (z214 % MOD)) % MOD
        a[pos + 15] = (z199) % MOD
        weight = weight * rates[(i + 1 & -(i + 1)).bit_length() - 1] % MOD
    del b
    _convolution_ntt998_butterfly_inv(a, stride=16)
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
            return _convolution_large_convolution_multiply_four_lanes(first, second, 1 << 21)
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
