"""998244353 固定の高速NTTと係数畳み込み。

`multiply(first, second)` は2つの昇べき順係数列を畳み込み、長さ
`len(first) + len(second) - 1` の係数列を返す。汎用mod判定、原始根探索、
CRTを通らず、固定したradix-4の変換表だけを使う。
"""
from array import array
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
    first = array('I', [1]) * count
    second = array('I', [1]) * count
    third = array('I', [1]) * count
    rotation = 1
    for block in range(count):
        first[block] = rotation
        second[block] = rotation * rotation % MOD
        third[block] = second[block] * rotation % MOD
        rotation = rotation * rate3[(~block & -~block).bit_length()] % MOD
    count = max(1, size >> 1)
    binary = array('I', [1]) * count
    rotation = 1
    for block in range(count):
        binary[block] = rotation
        rotation = rotation * rate2[(~block & -~block).bit_length()] % MOD
    return (binary, first, second, third)

def _convolution_ntt998_butterfly(values, tables=None):
    """In-place forward radix-4 NTT without coefficient normalization."""
    size = len(values)
    _convolution_ntt998_check_length(size)
    if size == 1:
        values[0] %= MOD
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
            width = 1 << height - level - 1
            rotation = 1
            for block in range(1 << level):
                if tables is not None:
                    rotation = binary[block]
                offset = block << height - level
                for index in range(width):
                    left = values[offset + index]
                    right = values[offset + index + width] * rotation
                    values[offset + index] = (left + right) % mod
                    values[offset + index + width] = (left - right) % mod
                if tables is None:
                    rotation = rotation * rate2[(~block & -~block).bit_length()] % mod
            level += 1
        else:
            width = 1 << height - level - 2
            rotation = 1
            for block in range(1 << level):
                if tables is None:
                    rotation2 = rotation * rotation % mod
                    rotation3 = rotation2 * rotation % mod
                else:
                    rotation = first[block]
                    rotation2 = second[block]
                    rotation3 = third[block]
                offset = block << height - level
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

def _convolution_ntt998_butterfly_inv(values, tables=None, keep_bit=0):
    """In-place inverse radix-4 transform without division by the length."""
    size = len(values)
    _convolution_ntt998_check_length(size)
    if size == 1:
        values[0] %= MOD
        return values
    if tables is not None:
        (binary, first, second, third) = tables
    height = (size - 1).bit_length()
    level = height
    mod = MOD
    inverse_imag = _convolution_ntt998_IIMAG
    irate2 = _convolution_ntt998_IRATE2
    irate3 = _convolution_ntt998_IRATE3
    while level:
        if level == 1:
            width = 1 << height - level
            limited = keep_bit and width > keep_bit
            mask = -keep_bit if limited else 0
            count = width >> bool(limited)
            rotation = 1
            for block in range(1 << level - 1):
                if tables is not None:
                    rotation = binary[block]
                offset = block << height - level + 1
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
            width = 1 << height - level
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
                offset = block << height - level + 2
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
'各位置の下限・上限を満たす広義単調増加列を数える。'
from bisect import bisect_right
DEFAULT_MOD = 998244353

def _fps_increasing_sequences_cross(values, length, factorial, inverse):
    size = len(values)
    if length == 1:
        return [sum(values) % DEFAULT_MOD]
    if size == 1:
        return values * length
    weighted = [value * inverse[size - 1 - i] % DEFAULT_MOD for (i, value) in enumerate(values)]
    if min(size, length) <= 32:
        product = multiply(weighted, factorial[:size + length - 1])
    else:
        count = size + length - 1
        transform_size = 1 << (count - 1).bit_length()
        product = factorial[:count] + [0] * (transform_size - count)
        weighted.extend([0] * (transform_size - size))
        ntt(product)
        ntt(weighted)
        for i in range(transform_size):
            product[i] = product[i] * weighted[i] % DEFAULT_MOD
        intt(product)
    return [product[size - 1 + i] * inverse[i] % DEFAULT_MOD for i in range(length)]

def _fps_increasing_sequences_parallel(values, distance, factorial, inverse):
    size = len(values)
    if distance == 0:
        result = []
        total = 0
        for value in values:
            total = (total + value) % DEFAULT_MOD
            result.append(total)
        return result
    scale = inverse[distance]
    kernel = [factorial[distance + i] * inverse[i] % DEFAULT_MOD * scale % DEFAULT_MOD for i in range(size)]
    return multiply(values, kernel)[:size]

def _fps_increasing_sequences_staircase(heights, start, factorial, inverse):
    stack = [(0, heights, start)]
    result = []
    mod = DEFAULT_MOD
    while stack:
        task = stack.pop()
        stage = task[0]
        if stage == 2:
            result = task[1] + result
            continue
        (heights, start) = task[1:3]
        size = len(heights)
        height = heights[-1]
        if stage == 0:
            if size == 1:
                result = [start[0]] * (height + 1)
            elif size == 2:
                result = [(start[0] * min(i + 1, heights[0] + 1) + start[1]) % mod for i in range(height + 1)]
            elif size * (height + 1) <= 4096:
                result = [0] * (height + 1)
                for (limit, value) in zip(heights, start):
                    for i in range(limit + 1):
                        value += result[i]
                        if value >= mod:
                            value -= mod
                        result[i] = value
            elif heights[0] == height:
                result = _fps_increasing_sequences_cross(start, height + 1, factorial, inverse)
            else:
                middle = size // 2
                stack.append((1, heights, start))
                stack.append((0, heights[:middle + 1], start[:middle] + [0]))
        else:
            middle = size // 2
            split = heights[middle]
            for i in range(len(result) - 1, 0, -1):
                result[i] = (result[i] - result[i - 1]) % mod
            bottom = start[middle:]
            top = _fps_increasing_sequences_cross(result, size - middle, factorial, inverse)
            right = _fps_increasing_sequences_parallel(result, size - middle - 1, factorial, inverse)
            bottom_right = _fps_increasing_sequences_cross(bottom, split + 1, factorial, inverse)
            bottom_top = _fps_increasing_sequences_parallel(bottom, split, factorial, inverse)
            prefix = [(right[i] + bottom_right[i]) % mod for i in range(split)]
            top = [(x + y) % mod for (x, y) in zip(top, bottom_top)]
            for i in range(len(top) - 1, 0, -1):
                top[i] = (top[i] - top[i - 1]) % mod
            stack.append((2, prefix))
            stack.append((0, [value - split for value in heights[middle:]], top))
    return result

def _fps_increasing_sequences_count_fast(lower, upper):
    mod = DEFAULT_MOD
    size = len(lower)
    lower = [lower[0]] + lower
    upper = [value - 1 for value in upper] + [upper[-1]]
    bound = size + upper[-1] + 2
    if bound > 1 << 22:
        raise ValueError('len(lower) + normalized width + 2 must not exceed 2^22')
    factorial = [1] * bound
    for i in range(1, bound):
        factorial[i] = factorial[i - 1] * i % mod
    inverse = [1] * bound
    inverse[-1] = pow(factorial[-1], mod - 2, mod)
    for i in range(bound - 1, 0, -1):
        inverse[i - 1] = inverse[i] * i % mod
    left = 0
    bottom = lower[0]
    right = bisect_right(lower, bottom) - 1
    top = bottom if right else upper[0]
    values = [1] + [0] * (right - left + top - bottom)
    while right != size or top != upper[-1]:
        for i in range(len(values) - 1, 0, -1):
            if i == 1 and left == 0 and (bottom == 0):
                break
            values[i] = (values[i] - values[i - 1]) % mod
        if bottom == top:
            heights = [value - bottom for value in upper[left:right + 1]]
            values = _fps_increasing_sequences_staircase(heights, values, factorial, inverse)
            left = right
            bottom = top
            top = upper[right]
        else:
            heights = [bisect_right(lower, i) - left for i in range(bottom, top + 1)]
            offset = heights[0]
            heights = [value - offset for value in heights]
            values = _fps_increasing_sequences_staircase(heights, values, factorial, inverse)
            left = right
            bottom = top
            right = bisect_right(lower, top) - 1
    return values[-1]

def count_increasing_sequences(lower, upper, mod=DEFAULT_MOD):
    """Count lower[i] <= x[i] < upper[i] with x nondecreasing, modulo mod."""
    if mod <= 0:
        raise ValueError('mod must be positive')
    if len(lower) != len(upper):
        raise ValueError('bound lengths differ')
    size = len(lower)
    if size == 0:
        return 1 % mod
    lower = list(lower)
    upper = list(upper)
    for index in range(1, size):
        if lower[index] < lower[index - 1]:
            lower[index] = lower[index - 1]
    for index in range(size - 2, -1, -1):
        if upper[index] > upper[index + 1]:
            upper[index] = upper[index + 1]
    for (left, right) in zip(lower, upper):
        if left >= right:
            return 0
    if size == 1:
        return (upper[0] - lower[0]) % mod
    offset = lower[0]
    lower = [value - offset for value in lower]
    upper = [value - offset for value in upper]
    width = upper[-1]
    if width == 1:
        return 1 % mod
    if mod == DEFAULT_MOD and size * width > 4096:
        return _fps_increasing_sequences_count_fast(lower, upper)
    values = [0] * width
    for value in range(lower[0], upper[0]):
        values[value] = 1
    for index in range(1, size):
        running = 0
        left = lower[index]
        right = upper[index]
        for value in range(width):
            running += values[value]
            if running >= mod:
                running -= mod
            values[value] = running if left <= value < right else 0
    return sum(values) % mod
import sys

def main():
    read = sys.stdin.buffer.readline
    (n, m) = map(int, read().split())
    lower = list(map(int, read().split()))
    upper = list(map(int, read().split()))
    print(count_increasing_sequences(lower, upper))
if __name__ == '__main__':
    main()
