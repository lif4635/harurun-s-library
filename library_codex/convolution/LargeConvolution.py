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


def _multiply_four_lanes(first, second, size):
    count = len(first) + len(second) - 1
    left = []
    for lane in range(4):
        work = [x % MOD for x in first[lane::4]]
        work.extend([0] * (size - len(work)))
        _butterfly(work)
        left.append(array("I", work))
    if first is second:
        right = left
    else:
        right = []
        for lane in range(4):
            work = [x % MOD for x in second[lane::4]]
            work.extend([0] * (size - len(work)))
            _butterfly(work)
            right.append(array("I", work))
    a0, a1, a2, a3 = left
    b0, b1, b2, b3 = right
    out = [array("I", [0]) * size for _ in range(4)]
    c0, c1, c2, c3 = out
    root = pow(3, (MOD - 1) // size, MOD)
    rates = [pow(root, (size >> (j + 1)) - (size - (size >> j)), MOD)
             for j in range(size.bit_length())]
    weight = 1
    for i in range(size):
        x0, x1, x2, x3 = a0[i], a1[i], a2[i], a3[i]
        y0, y1, y2, y3 = b0[i], b1[i], b2[i], b3[i]
        c0[i] = (x0 * y0 + weight * ((x1 * y3 + x2 * y2 + x3 * y1) % MOD)) % MOD
        c1[i] = (x0 * y1 + x1 * y0 + weight * ((x2 * y3 + x3 * y2) % MOD)) % MOD
        c2[i] = (x0 * y2 + x1 * y1 + x2 * y0 + weight * (x3 * y3 % MOD)) % MOD
        c3[i] = (x0 * y3 + x1 * y2 + x2 * y1 + x3 * y0) % MOD
        weight = weight * rates[((i + 1) & -(i + 1)).bit_length() - 1] % MOD
    del left, right, a0, a1, a2, a3, b0, b1, b2, b3, work, c0, c1, c2, c3
    inverse = pow(size, MOD - 2, MOD)
    result = [0] * count
    for lane in range(4):
        work = list(out[lane])
        out[lane] = None
        _butterfly_inv(work)
        for j in range((count - lane + 3) // 4):
            result[j * 4 + lane] = work[j] * inverse % MOD
    return result


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
            return _multiply_four_lanes(first, second, 1 << 23)
    block = min(1 << 22, 1 << (shorter - 1).bit_length())
    return _multiply_blocks(first, second, block)
