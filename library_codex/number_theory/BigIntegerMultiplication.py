"""符号付き10進・16進文字列を、浮動小数点を使わず高速に乗算する。"""

from library_codex.convolution.NTT998 import multiply
from library_codex.convolution.NTT import convolution_ntt


def _parts(value, radix):
    negative = value.startswith("-")
    if value[:1] in ("+", "-"):
        value = value[1:]
    if not value or not value.isascii():
        raise ValueError("expected a signed integer string")
    if radix == 10:
        valid = value.isdecimal()
    else:
        valid = not value.strip("0123456789abcdefABCDEF")
    if not valid:
        raise ValueError("invalid digit")
    return negative, value.lstrip("0") or "0"


def _product(first, second, radix, width):
    if first == "0" or second == "0":
        return "0"
    if len(first) + len(second) <= 512:
        value = int(first, radix) * int(second, radix)
        return str(value) if radix == 10 else format(value, "X")
    base = radix ** width
    a = [int(first[max(0, i - width):i], radix)
         for i in range(len(first), 0, -width)]
    b = a if first == second else [int(second[max(0, i - width):i], radix)
                                  for i in range(len(second), 0, -width)]
    length = len(a) + len(b) - 1
    if min(len(a), len(b)) <= 32:
        if len(a) > len(b):
            a, b = b, a
        result = [0] * length
        for i, value in enumerate(a):
            for j, other in enumerate(b):
                result[i + j] += value * other
    else:
        if length > 1 << 23:
            raise ValueError("convolution length exceeds 2^23")
        result = multiply(a, b)
        other = convolution_ntt(a, b, 469762049, 3)
        inverse = pow(998244353, -1, 469762049)
        for i in range(length):
            result[i] += 998244353 * ((other[i] - result[i]) * inverse % 469762049)
    carry = 0
    for i in range(length):
        carry, result[i] = divmod(result[i] + carry, base)
    while carry:
        carry, value = divmod(carry, base)
        result.append(value)
    while result and result[-1] == 0:
        result.pop()
    if radix == 10:
        return str(result[-1]) + "".join(str(value).zfill(width) for value in reversed(result[:-1]))
    return format(result[-1], "X") + "".join(format(value, "X").zfill(width) for value in reversed(result[:-1]))


def multiply_decimal(first, second):
    """符号付き10進文字列同士の積を、先頭0のない10進文字列で返す。O(N log N)。"""
    negative, first = _parts(first, 10)
    other_negative, second = _parts(second, 10)
    result = _product(first, second, 10, 5)
    return "-" + result if negative != other_negative and result != "0" else result


def multiply_hex(first, second):
    """符号付き16進文字列同士の積を、大文字・先頭0なしの16進文字列で返す。O(N log N)。"""
    negative, first = _parts(first, 16)
    other_negative, second = _parts(second, 16)
    result = _product(first.upper(), second.upper(), 16, 4)
    return "-" + result if negative != other_negative and result != "0" else result
