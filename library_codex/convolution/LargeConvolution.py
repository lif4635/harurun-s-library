"""出力が2^23項を超える係数列も、998244353で畳み込む。

各入力を分割して順NTTを再利用し、同じ出力位置へ寄与する積を
周波数表現でまとめてから逆変換する。通常サイズはNTT998を使う。
"""

from array import array

from library_codex.convolution.NTT998 import (
    MOD,
    _IMAG,
    _IIMAG,
    _RATE2,
    _IRATE2,
    _butterfly,
    _butterfly_inv,
    multiply as _multiply,
)


_TILE_FORWARD_EIGHTH = pow(3, (MOD - 1) // 8, MOD)
_TILE_FORWARD_THIRD = pow(_TILE_FORWARD_EIGHTH, 3, MOD)
_TILE_FORWARD_RATES = [pow(3, (3 * ((MOD - 1) >> (t + 4)) - (MOD - 1) // 8) % (MOD - 1), MOD) for t in range(21)]
_TILE_INVERSE_EIGHTH = pow(3, MOD - 1 - (MOD - 1) // 8, MOD)
_TILE_INVERSE_THIRD = pow(_TILE_INVERSE_EIGHTH, 3, MOD)
_TILE_INVERSE_RATES = [pow(3, (-3 * ((MOD - 1) >> (t + 4)) + (MOD - 1) // 8) % (MOD - 1), MOD) for t in range(21)]


def _tile_rotation(block, bits, extra, inverse):
    exponent = 0
    for _ in range(bits):
        exponent = (exponent << 1) | (block & 1)
        block >>= 1
    exponent *= (MOD - 1) >> (bits + extra)
    return pow(3, -exponent % (MOD - 1) if inverse else exponent, MOD)


def _pad_forward(values, scale, stride, size, packed=False):
    total = stride * size
    result = array("I", [0]) * total if packed else [0] * total
    n = len(values)
    if size < 8 or n > total // 2:
        for i in range(n):
            result[i] = values[i] * scale % MOD
        return _butterfly8(result, stride)
    width = total // 8
    imag = _IMAG
    eighth = pow(3, (MOD - 1) // 8, MOD)
    third = pow(eighth, 3, MOD)
    for i in range(width):
        x0 = values[i] * scale % MOD if i < n else 0
        x1 = values[i + width] * scale % MOD if i + width < n else 0
        x2 = values[i + 2 * width] * scale % MOD if i + 2 * width < n else 0
        x3 = values[i + 3 * width] * scale % MOD if i + 3 * width < n else 0
        v1 = x1 * eighth
        v2 = x2 * imag
        v3 = x3 * third
        d0 = (x1 - x3) * imag
        d1 = x1 * third + x3 * eighth
        result[i] = (x0 + x2 + x1 + x3) % MOD
        result[i + width] = (x0 + x2 - x1 - x3) % MOD
        result[i + 2 * width] = (x0 - x2 + d0) % MOD
        result[i + 3 * width] = (x0 - x2 - d0) % MOD
        result[i + 4 * width] = (x0 + v2 + v1 + v3) % MOD
        result[i + 5 * width] = (x0 + v2 - v1 - v3) % MOD
        result[i + 6 * width] = (x0 - v2 + d1) % MOD
        result[i + 7 * width] = (x0 - v2 - d1) % MOD
    return _butterfly8(result, stride, 3)


def _append_block(result, work, start, output_size, inverse_size):
    overlap = len(result) - start
    for k in range(overlap):
        value = result[start + k] + work[k] * inverse_size % MOD
        result[start + k] = value - MOD if value >= MOD else value
    for k in range(overlap, min(len(work) - 1, output_size - start)):
        result.append(work[k] * inverse_size % MOD)


def _multiply_short_blocks(first, second, block):
    size = block << 1
    output_size = len(first) + len(second) - 1
    inverse_size = pow(size, MOD - 2, MOD)
    fixed = [value % MOD for value in first]
    fixed.extend([0] * (size - len(fixed)))
    _butterfly(fixed)
    result = []
    for start in range(0, len(second), block):
        work = [value % MOD for value in second[start:start + block]]
        work.extend([0] * (size - len(work)))
        _butterfly(work)
        for k in range(size):
            work[k] = work[k] * fixed[k] % MOD
        _butterfly_inv(work)
        _append_block(result, work, start, output_size, inverse_size)
    return result


def _multiply_blocks(first, second, block):
    if len(first) <= block < len(second):
        return _multiply_short_blocks(first, second, block)
    if len(second) <= block < len(first):
        return _multiply_short_blocks(second, first, block)
    size = block << 1
    output_size = len(first) + len(second) - 1
    same = first is second

    def transform(values):
        blocks = []
        for start in range(0, len(values), block):
            work = [value % MOD for value in values[start:start + block]]
            work.extend([0] * (size - len(work)))
            _butterfly(work)
            blocks.append(array("I", work))
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
        _butterfly_inv(work)
        start = diagonal * block
        _append_block(result, work, start, output_size, inverse_size)
        expired = diagonal - len(right) + 1
        if expired >= 0:
            left[expired] = None
        expired = diagonal - len(left) + 1
        if expired >= 0 and not same:
            right[expired] = None
    return result


def _butterfly8_range(values, stride, start, stop, begin, end):
    size = len(values) // stride
    if size == 1:
        for i in range(len(values)):
            values[i] %= MOD
        return values
    height = size.bit_length() - 1
    mod = MOD
    imag = _IMAG
    eighth = _TILE_FORWARD_EIGHTH
    third = _TILE_FORWARD_THIRD
    rates = _TILE_FORWARD_RATES
    level = start
    while level < stop:
        if height - level < 3:
            width = stride << (height - level - 1)
            first = begin // (width << 1)
            last = end // (width << 1)
            rotation = _tile_rotation(first, level, 1, False)
            for block in range(first, last):
                offset = (block << (height - level)) * stride
                for index in range(width):
                    pos = offset + index
                    x = values[pos]
                    y = values[pos + width] * rotation
                    values[pos] = (x + y) % mod
                    values[pos + width] = (x - y) % mod
                rotation = rotation * _RATE2[(~block & -~block).bit_length()] % mod
            level += 1
        else:
            width = stride << (height - level - 3)
            first = begin // (width << 3)
            last = end // (width << 3)
            rotation = _tile_rotation(first, level, 3, False)
            for block in range(first, last):
                r2 = rotation * rotation % mod
                r3 = r2 * rotation % mod
                r4 = r2 * r2 % mod
                r5 = r4 * rotation % mod
                r6 = r4 * r2 % mod
                r7 = r4 * r3 % mod
                s1 = rotation * imag % mod
                s2 = r2 * imag % mod
                s3 = r3 * imag % mod
                s5 = r5 * imag % mod
                s6 = r6 * imag % mod
                s7 = r7 * imag % mod
                e1 = rotation * eighth % mod
                e3 = r3 * eighth % mod
                e5 = r5 * eighth % mod
                e7 = r7 * eighth % mod
                t1 = rotation * third % mod
                t3 = r3 * third % mod
                t5 = r5 * third % mod
                t7 = r7 * third % mod
                offset = (block << (height - level)) * stride
                for index in range(width):
                    pos = offset + index
                    x0 = values[pos]
                    x1 = values[pos + 1 * width]
                    x2 = values[pos + 2 * width]
                    x3 = values[pos + 3 * width]
                    x4 = values[pos + 4 * width]
                    x5 = values[pos + 5 * width]
                    x6 = values[pos + 6 * width]
                    x7 = values[pos + 7 * width]
                    u0 = x0 + x4 * r4
                    u1 = x1 * rotation + x5 * r5
                    u2 = x2 * r2 + x6 * r6
                    u3 = x3 * r3 + x7 * r7
                    v0 = x0 - x4 * r4
                    v1 = x1 * e1 - x5 * e5
                    v2 = x2 * s2 - x6 * s6
                    v3 = x3 * t3 - x7 * t7
                    d0 = x1 * s1 + x5 * s5 - x3 * s3 - x7 * s7
                    d1 = x1 * t1 - x5 * t5 + x3 * e3 - x7 * e7
                    values[pos] = (u0 + u2 + u1 + u3) % mod
                    values[pos + width] = (u0 + u2 - u1 - u3) % mod
                    values[pos + 2 * width] = (u0 - u2 + d0) % mod
                    values[pos + 3 * width] = (u0 - u2 - d0) % mod
                    values[pos + 4 * width] = (v0 + v2 + v1 + v3) % mod
                    values[pos + 5 * width] = (v0 + v2 - v1 - v3) % mod
                    values[pos + 6 * width] = (v0 - v2 + d1) % mod
                    values[pos + 7 * width] = (v0 - v2 - d1) % mod
                if block + 1 < 1 << level:
                    rotation = rotation * rates[(~block & -~block).bit_length() - 1] % mod
            level += 3
    return values


def _butterfly8(values, stride=16, start=0):
    height = (len(values) // stride).bit_length() - 1
    cut = max(start, (height - 9) // 3 * 3)
    if cut == 0:
        return _butterfly8_range(values, stride, start, height, 0, len(values))
    span = stride << (height - cut)
    _butterfly8_range(values, stride, start, cut, 0, len(values))
    for begin in range(0, len(values), span):
        _butterfly8_range(values, stride, cut, height, begin, begin + span)
    return values


def _butterfly8_inv_range(values, stride, start, stop, begin, end):
    size = len(values) // stride
    if size == 1:
        for i in range(len(values)):
            values[i] %= MOD
        return values
    height = size.bit_length() - 1
    mod = MOD
    imag = _IIMAG
    eighth = _TILE_INVERSE_EIGHTH
    third = _TILE_INVERSE_THIRD
    rates = _TILE_INVERSE_RATES
    level = start
    while level > stop:
        if level < 3:
            width = stride << (height - level)
            first = begin // (width << 1)
            last = end // (width << 1)
            rotation = _tile_rotation(first, level - 1, 1, True)
            for block in range(first, last):
                offset = (block << (height - level + 1)) * stride
                for index in range(width):
                    pos = offset + index
                    x = values[pos]
                    y = values[pos + width]
                    values[pos] = (x + y) % mod
                    values[pos + width] = (x - y) * rotation % mod
                rotation = rotation * _IRATE2[(~block & -~block).bit_length()] % mod
            level -= 1
        else:
            width = stride << (height - level)
            first = begin // (width << 3)
            last = end // (width << 3)
            rotation = _tile_rotation(first, level - 3, 3, True)
            for block in range(first, last):
                r2 = rotation * rotation % mod
                r3 = r2 * rotation % mod
                r4 = r2 * r2 % mod
                r5 = r4 * rotation % mod
                r6 = r4 * r2 % mod
                r7 = r4 * r3 % mod
                s1 = rotation * imag % mod
                s2 = r2 * imag % mod
                s3 = r3 * imag % mod
                s5 = r5 * imag % mod
                s6 = r6 * imag % mod
                s7 = r7 * imag % mod
                e1 = rotation * eighth % mod
                e3 = r3 * eighth % mod
                e5 = r5 * eighth % mod
                e7 = r7 * eighth % mod
                t1 = rotation * third % mod
                t3 = r3 * third % mod
                t5 = r5 * third % mod
                t7 = r7 * third % mod
                offset = (block << (height - level + 3)) * stride
                for index in range(width):
                    pos = offset + index
                    x0 = values[pos]
                    x1 = values[pos + width]
                    x2 = values[pos + 2 * width]
                    x3 = values[pos + 3 * width]
                    x4 = values[pos + 4 * width]
                    x5 = values[pos + 5 * width]
                    x6 = values[pos + 6 * width]
                    x7 = values[pos + 7 * width]
                    u0 = x0 + x1 + x2 + x3
                    u1 = x0 - x1
                    u2 = x0 + x1 - x2 - x3
                    u3 = x2 - x3
                    v0 = x4 + x5 + x6 + x7
                    v1 = x4 - x5
                    v2 = x4 + x5 - x6 - x7
                    v3 = x6 - x7
                    values[pos] = (u0 + v0) % mod
                    values[pos + width] = (u1 * rotation + u3 * s1 + v1 * e1 + v3 * t1) % mod
                    values[pos + 2 * width] = (u2 * r2 + v2 * s2) % mod
                    values[pos + 3 * width] = (u1 * r3 - u3 * s3 + v1 * t3 + v3 * e3) % mod
                    values[pos + 4 * width] = (u0 - v0) * r4 % mod
                    values[pos + 5 * width] = (u1 * r5 + u3 * s5 - v1 * e5 - v3 * t5) % mod
                    values[pos + 6 * width] = (u2 * r6 - v2 * s6) % mod
                    values[pos + 7 * width] = (u1 * r7 - u3 * s7 - v1 * t7 - v3 * e7) % mod
                if block + 1 < 1 << (level - 3):
                    rotation = rotation * rates[(~block & -~block).bit_length() - 1] % mod
            level -= 3
    return values


def _butterfly8_inv(values, stride=16):
    height = (len(values) // stride).bit_length() - 1
    cut = max(0, height - 9)
    if cut == 0:
        return _butterfly8_inv_range(values, stride, height, 0, 0, len(values))
    span = stride << (height - cut)
    for begin in range(0, len(values), span):
        _butterfly8_inv_range(values, stride, height, cut, begin, begin + span)
    _butterfly8_inv_range(values, stride, cut, 0, 0, len(values))
    return values


def _multiply_sixteen_lanes(first, second, size, packed=None):
    count = len(first) + len(second) - 1
    inverse = pow(size, MOD - 2, MOD)
    if packed is None:
        packed = size == 1 << 20
    a = _pad_forward(first, 1, 16, size, packed)
    if first is second:
        b = a
    else:
        b = _pad_forward(second, inverse, 16, size, packed)
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
        a[pos + 15] = (c15) % MOD
        weight = weight * rates[((i + 1) & -(i + 1)).bit_length() - 1] % MOD
    del b
    _butterfly8_inv(a, 16)
    if first is second:
        for i in range(count):
            a[i] = a[i] * inverse % MOD
    del a[count:]
    return list(a) if packed else a


def multiply(first, second):
    """昇べき係数列の積をmod 998244353で返す。入力は変更しない。"""

    if not first or not second:
        return []
    shorter = min(len(first), len(second))
    if len(first) + len(second) - 1 <= 1 << 23 or shorter <= 60:
        return _multiply(first, second)
    if (len(first) + len(second) - 2).bit_length() == 24 and shorter > 1 << 21:
        blocks = (len(first) + (1 << 22) - 1) // (1 << 22)
        blocks += (len(second) + (1 << 22) - 1) // (1 << 22)
        if blocks >= 4:
            return _multiply_sixteen_lanes(first, second, 1 << 20)
    if (len(first) + len(second) - 2).bit_length() == 25:
        blocks = (len(first) + (1 << 22) - 1) // (1 << 22)
        blocks += (len(second) + (1 << 22) - 1) // (1 << 22)
        if blocks >= 7:
            return _multiply_sixteen_lanes(first, second, 1 << 21)
    block = min(1 << 22, 1 << (shorter - 1).bit_length())
    return _multiply_blocks(first, second, block)
