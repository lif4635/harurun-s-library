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

def _convolution_ntt998_butterfly_unrolled(values, tables=None, stride=1):
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
                if stride >= 2:
                    for start in range(0, width, 2):
                        index = start + 0
                        left = values[offset + index]
                        right = values[offset + index + width] * rotation
                        values[offset + index] = (left + right) % mod
                        values[offset + index + width] = (left - right) % mod
                        index = start + 1
                        left = values[offset + index]
                        right = values[offset + index + width] * rotation
                        values[offset + index] = (left + right) % mod
                        values[offset + index + width] = (left - right) % mod
                else:
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
                if stride >= 2:
                    for start in range(0, width, 2):
                        index = start + 0
                        value0 = values[offset + index]
                        value1 = values[offset + index + width] * rotation
                        value2 = values[offset + index + 2 * width] * rotation2
                        value3 = values[offset + index + 3 * width] * rotation3
                        difference = (value1 - value3) % mod * imag
                        values[offset + index] = (value0 + value2 + value1 + value3) % mod
                        values[offset + index + width] = (value0 + value2 - value1 - value3) % mod
                        values[offset + index + 2 * width] = (value0 - value2 + difference) % mod
                        values[offset + index + 3 * width] = (value0 - value2 - difference) % mod
                        index = start + 1
                        value0 = values[offset + index]
                        value1 = values[offset + index + width] * rotation
                        value2 = values[offset + index + 2 * width] * rotation2
                        value3 = values[offset + index + 3 * width] * rotation3
                        difference = (value1 - value3) % mod * imag
                        values[offset + index] = (value0 + value2 + value1 + value3) % mod
                        values[offset + index + width] = (value0 + value2 - value1 - value3) % mod
                        values[offset + index + 2 * width] = (value0 - value2 + difference) % mod
                        values[offset + index + 3 * width] = (value0 - value2 - difference) % mod
                else:
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

def _convolution_ntt998_butterfly_inv_unrolled(values, tables=None, keep_bit=0, stride=1):
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
                if stride >= 2 and not keep_bit:
                    for start in range(0, count, 2):
                        position = start + 0
                        index = position + (position & mask)
                        left = values[offset + index]
                        right = values[offset + index + width]
                        values[offset + index] = (left + right) % mod
                        values[offset + index + width] = (left - right) * rotation % mod
                        position = start + 1
                        index = position + (position & mask)
                        left = values[offset + index]
                        right = values[offset + index + width]
                        values[offset + index] = (left + right) % mod
                        values[offset + index + width] = (left - right) * rotation % mod
                else:
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
                if stride >= 2 and not keep_bit:
                    for start in range(0, count, 2):
                        position = start + 0
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
                        position = start + 1
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
                else:
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
    a = [0] * (16 * size)
    for i in range(len(first)):
        a[i] = first[i] % MOD
    _convolution_ntt998_butterfly_unrolled(a, stride=16)
    if first is second:
        b = a
    else:
        b = [0] * (16 * size)
        for i in range(len(second)):
            b[i] = second[i] * inverse % MOD
        _convolution_ntt998_butterfly_unrolled(b, stride=16)
    root = pow(3, (MOD - 1) // size, MOD)
    rates = [pow(root, (size >> j + 1) - (size - (size >> j)), MOD) for j in range(size.bit_length())]
    weight = 1
    for i in range(size):
        pos = i << 4
        (x0, y0) = (a[pos + 0], b[pos + 0])
        (x1, y1) = (a[pos + 1], b[pos + 1])
        (x2, y2) = (a[pos + 2], b[pos + 2])
        (x3, y3) = (a[pos + 3], b[pos + 3])
        (x4, y4) = (a[pos + 4], b[pos + 4])
        (x5, y5) = (a[pos + 5], b[pos + 5])
        (x6, y6) = (a[pos + 6], b[pos + 6])
        (x7, y7) = (a[pos + 7], b[pos + 7])
        (x8, y8) = (a[pos + 8], b[pos + 8])
        (x9, y9) = (a[pos + 9], b[pos + 9])
        (x10, y10) = (a[pos + 10], b[pos + 10])
        (x11, y11) = (a[pos + 11], b[pos + 11])
        (x12, y12) = (a[pos + 12], b[pos + 12])
        (x13, y13) = (a[pos + 13], b[pos + 13])
        (x14, y14) = (a[pos + 14], b[pos + 14])
        (x15, y15) = (a[pos + 15], b[pos + 15])
        c0 = x0 * y0
        c1 = x0 * y1 + x1 * y0
        c2 = x0 * y2 + x1 * y1 + x2 * y0
        c3 = x0 * y3 + x1 * y2 + x2 * y1 + x3 * y0
        c4 = x0 * y4 + x1 * y3 + x2 * y2 + x3 * y1 + x4 * y0
        c5 = x0 * y5 + x1 * y4 + x2 * y3 + x3 * y2 + x4 * y1 + x5 * y0
        c6 = x0 * y6 + x1 * y5 + x2 * y4 + x3 * y3 + x4 * y2 + x5 * y1 + x6 * y0
        c7 = x0 * y7 + x1 * y6 + x2 * y5 + x3 * y4 + x4 * y3 + x5 * y2 + x6 * y1 + x7 * y0
        c8 = x0 * y8 + x1 * y7 + x2 * y6 + x3 * y5 + x4 * y4 + x5 * y3 + x6 * y2 + x7 * y1 + x8 * y0
        c9 = x0 * y9 + x1 * y8 + x2 * y7 + x3 * y6 + x4 * y5 + x5 * y4 + x6 * y3 + x7 * y2 + x8 * y1 + x9 * y0
        c10 = x0 * y10 + x1 * y9 + x2 * y8 + x3 * y7 + x4 * y6 + x5 * y5 + x6 * y4 + x7 * y3 + x8 * y2 + x9 * y1 + x10 * y0
        c11 = x0 * y11 + x1 * y10 + x2 * y9 + x3 * y8 + x4 * y7 + x5 * y6 + x6 * y5 + x7 * y4 + x8 * y3 + x9 * y2 + x10 * y1 + x11 * y0
        c12 = x0 * y12 + x1 * y11 + x2 * y10 + x3 * y9 + x4 * y8 + x5 * y7 + x6 * y6 + x7 * y5 + x8 * y4 + x9 * y3 + x10 * y2 + x11 * y1 + x12 * y0
        c13 = x0 * y13 + x1 * y12 + x2 * y11 + x3 * y10 + x4 * y9 + x5 * y8 + x6 * y7 + x7 * y6 + x8 * y5 + x9 * y4 + x10 * y3 + x11 * y2 + x12 * y1 + x13 * y0
        c14 = x0 * y14 + x1 * y13 + x2 * y12 + x3 * y11 + x4 * y10 + x5 * y9 + x6 * y8 + x7 * y7 + x8 * y6 + x9 * y5 + x10 * y4 + x11 * y3 + x12 * y2 + x13 * y1 + x14 * y0
        c15 = x0 * y15 + x1 * y14 + x2 * y13 + x3 * y12 + x4 * y11 + x5 * y10 + x6 * y9 + x7 * y8 + x8 * y7 + x9 * y6 + x10 * y5 + x11 * y4 + x12 * y3 + x13 * y2 + x14 * y1 + x15 * y0
        c16 = x1 * y15 + x2 * y14 + x3 * y13 + x4 * y12 + x5 * y11 + x6 * y10 + x7 * y9 + x8 * y8 + x9 * y7 + x10 * y6 + x11 * y5 + x12 * y4 + x13 * y3 + x14 * y2 + x15 * y1
        c17 = x2 * y15 + x3 * y14 + x4 * y13 + x5 * y12 + x6 * y11 + x7 * y10 + x8 * y9 + x9 * y8 + x10 * y7 + x11 * y6 + x12 * y5 + x13 * y4 + x14 * y3 + x15 * y2
        c18 = x3 * y15 + x4 * y14 + x5 * y13 + x6 * y12 + x7 * y11 + x8 * y10 + x9 * y9 + x10 * y8 + x11 * y7 + x12 * y6 + x13 * y5 + x14 * y4 + x15 * y3
        c19 = x4 * y15 + x5 * y14 + x6 * y13 + x7 * y12 + x8 * y11 + x9 * y10 + x10 * y9 + x11 * y8 + x12 * y7 + x13 * y6 + x14 * y5 + x15 * y4
        c20 = x5 * y15 + x6 * y14 + x7 * y13 + x8 * y12 + x9 * y11 + x10 * y10 + x11 * y9 + x12 * y8 + x13 * y7 + x14 * y6 + x15 * y5
        c21 = x6 * y15 + x7 * y14 + x8 * y13 + x9 * y12 + x10 * y11 + x11 * y10 + x12 * y9 + x13 * y8 + x14 * y7 + x15 * y6
        c22 = x7 * y15 + x8 * y14 + x9 * y13 + x10 * y12 + x11 * y11 + x12 * y10 + x13 * y9 + x14 * y8 + x15 * y7
        c23 = x8 * y15 + x9 * y14 + x10 * y13 + x11 * y12 + x12 * y11 + x13 * y10 + x14 * y9 + x15 * y8
        c24 = x9 * y15 + x10 * y14 + x11 * y13 + x12 * y12 + x13 * y11 + x14 * y10 + x15 * y9
        c25 = x10 * y15 + x11 * y14 + x12 * y13 + x13 * y12 + x14 * y11 + x15 * y10
        c26 = x11 * y15 + x12 * y14 + x13 * y13 + x14 * y12 + x15 * y11
        c27 = x12 * y15 + x13 * y14 + x14 * y13 + x15 * y12
        c28 = x13 * y15 + x14 * y14 + x15 * y13
        c29 = x14 * y15 + x15 * y14
        c30 = x15 * y15
        a[pos + 0] = (c0 + weight * (c16 % MOD)) % MOD
        a[pos + 1] = (c1 + weight * (c17 % MOD)) % MOD
        a[pos + 2] = (c2 + weight * (c18 % MOD)) % MOD
        a[pos + 3] = (c3 + weight * (c19 % MOD)) % MOD
        a[pos + 4] = (c4 + weight * (c20 % MOD)) % MOD
        a[pos + 5] = (c5 + weight * (c21 % MOD)) % MOD
        a[pos + 6] = (c6 + weight * (c22 % MOD)) % MOD
        a[pos + 7] = (c7 + weight * (c23 % MOD)) % MOD
        a[pos + 8] = (c8 + weight * (c24 % MOD)) % MOD
        a[pos + 9] = (c9 + weight * (c25 % MOD)) % MOD
        a[pos + 10] = (c10 + weight * (c26 % MOD)) % MOD
        a[pos + 11] = (c11 + weight * (c27 % MOD)) % MOD
        a[pos + 12] = (c12 + weight * (c28 % MOD)) % MOD
        a[pos + 13] = (c13 + weight * (c29 % MOD)) % MOD
        a[pos + 14] = (c14 + weight * (c30 % MOD)) % MOD
        a[pos + 15] = c15 % MOD
        weight = weight * rates[(i + 1 & -(i + 1)).bit_length() - 1] % MOD
    del b
    _convolution_ntt998_butterfly_inv_unrolled(a, stride=16)
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
            return _convolution_large_convolution_multiply_sixteen_lanes(first, second, 1 << 21)
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
