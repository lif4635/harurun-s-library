"""出力が2^23項を超える係数列も、998244353で畳み込む。

各入力を分割して順NTTを再利用し、同じ出力位置へ寄与する積を
周波数表現でまとめてから逆変換する。通常サイズはNTT998を使う。
"""

from array import array

from library_codex.convolution.NTT998 import (
    MOD,
    _butterfly,
    _butterfly_inv,
    multiply as _multiply,
)


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


def _multiply_sixteen_lanes(first, second, size):
    count = len(first) + len(second) - 1
    inverse = pow(size, MOD - 2, MOD)
    a = [0] * (16 * size)
    for i in range(len(first)):
        a[i] = first[i] % MOD
    _butterfly(a, stride=16)
    if first is second:
        b = a
    else:
        b = [0] * (16 * size)
        for i in range(len(second)):
            b[i] = second[i] * inverse % MOD
        _butterfly(b, stride=16)
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
        weight = weight * rates[(i + 1 & -(i + 1)).bit_length() - 1] % MOD
    del b
    _butterfly_inv(a, stride=16)
    if first is second:
        for i in range(count):
            a[i] = a[i] * inverse % MOD
    del a[count:]
    return a


def multiply(first, second):
    """昇べき係数列の積をmod 998244353で返す。入力は変更しない。"""

    if not first or not second:
        return []
    shorter = min(len(first), len(second))
    if len(first) + len(second) - 1 <= 1 << 23 or shorter <= 60:
        return _multiply(first, second)
    if (len(first) + len(second) - 2).bit_length() == 25:
        blocks = (len(first) + (1 << 22) - 1) // (1 << 22)
        blocks += (len(second) + (1 << 22) - 1) // (1 << 22)
        if blocks >= 7:
            return _multiply_sixteen_lanes(first, second, 1 << 21)
    block = min(1 << 22, 1 << (shorter - 1).bit_length())
    return _multiply_blocks(first, second, block)
