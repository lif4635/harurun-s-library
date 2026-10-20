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


def multiply(first, second):
    """昇べき係数列の積をmod 998244353で返す。入力は変更しない。"""

    if not first or not second:
        return []
    shorter = min(len(first), len(second))
    if len(first) + len(second) - 1 <= 1 << 23 or shorter <= 60:
        return _multiply(first, second)
    block = min(1 << 22, 1 << (shorter - 1).bit_length())
    return _multiply_blocks(first, second, block)
