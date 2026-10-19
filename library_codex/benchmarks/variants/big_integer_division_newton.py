"""大きな整数の商と余りを、整数だけの逆数近似で求める。"""


def _reciprocal(value):
    bits = value.bit_length()
    levels = []
    width = bits
    while width > 128:
        levels.append(width)
        width = (width + 1) // 2
    inverse = (1 << (2 * width)) // (value >> (bits - width))
    for target in reversed(levels):
        prefix = value >> (bits - target)
        inverse = (inverse << (target - width + 1)) - (
            prefix * inverse * inverse >> (2 * width)
        )
        remainder = (1 << (2 * target)) - prefix * inverse
        while remainder < 0:
            inverse -= 1
            remainder += prefix
        while remainder >= prefix:
            inverse += 1
            remainder -= prefix
        width = target
    return inverse


def _positive(first, second, inverse=None):
    bits = second.bit_length()
    quotient_bits = first.bit_length() - bits
    if min(bits, quotient_bits) <= 2048:
        return divmod(first, second)
    width = bits if inverse is not None else min(bits, quotient_bits + 3)
    shift = bits - width
    if inverse is None:
        inverse = _reciprocal(second >> shift)
    if quotient_bits <= bits:
        quotient = ((first >> shift) * inverse) >> (2 * width)
    else:
        block = bits - 1
        count = (first.bit_length() + block - 1) // block
        chunks = [0] * count
        stack = [(first, 0, count)]
        while stack:
            value, left, right = stack.pop()
            if right - left == 1:
                chunks[left] = value
            else:
                middle = (left + right) // 2
                offset = (middle - left) * block
                high = value >> offset
                stack.append((high, middle, right))
                stack.append((value - (high << offset), left, middle))
        remainder = 0
        for i in range(count - 1, -1, -1):
            value = (remainder << block) + chunks[i]
            digit = (value * inverse) >> (2 * bits)
            remainder = value - digit * second
            if remainder >= second:
                digit += 1
                remainder -= second
            chunks[i] = digit
        step = 1
        while step < count:
            for i in range(0, count - step, 2 * step):
                chunks[i] += chunks[i + step] << (step * block)
            step *= 2
        return chunks[0], remainder
    remainder = first - quotient * second
    while remainder < 0:
        quotient -= 1
        remainder += second
    while remainder >= second:
        quotient += 1
        remainder -= second
    return quotient, remainder


def divmod_int(first, second):
    """Pythonのdivmodと同じ商・余りを返す。大入力は乗算ベースの除算を使う。"""
    if second == 0:
        raise ZeroDivisionError("integer division or modulo by zero")
    quotient, remainder = _positive(abs(first), abs(second))
    if (first < 0) != (second < 0):
        quotient = -quotient
        if remainder:
            quotient -= 1
            remainder = abs(second) - remainder
    if second < 0:
        remainder = -remainder
    return quotient, remainder


def _parse(value, radix, powers):
    negative = value.startswith("-")
    if value[:1] in ("+", "-"):
        value = value[1:]
    if not value or not value.isascii():
        raise ValueError("expected a signed integer string")
    if radix == 16:
        if value.strip("0123456789abcdefABCDEF"):
            raise ValueError("invalid hexadecimal digit")
        result = int(value, 16)
    else:
        if not value.isdecimal():
            raise ValueError("invalid decimal digit")
        value = value.lstrip("0") or "0"
        chunks = [int(value[max(0, i - 512):i]) for i in range(len(value), 0, -512)]
        level = 0
        while len(chunks) > 1:
            if level == len(powers):
                powers.append(powers[-1] * powers[-1])
            base = powers[level]
            count = len(chunks)
            chunks = [chunks[i] + chunks[i + 1] * base for i in range(0, count - 1, 2)] + (
                [chunks[-1]] if count & 1 else []
            )
            level += 1
        result = chunks[0]
    return -result if negative else result


def _decimal(value, powers, inverses):
    if not value:
        return "0"
    negative = value < 0
    value = abs(value)
    while powers[-1] <= value:
        powers.append(powers[-1] * powers[-1])
    level = len(powers) - 2
    while level >= 0 and powers[level] > value:
        level -= 1
    stack = [(value, level)]
    output = []
    while stack:
        current, level = stack.pop()
        if not current and not output:
            continue
        if level < 0:
            output.append(str(current).zfill(512) if output else str(current))
        else:
            shift = 512 << level
            base = powers[level] >> shift
            reduced = current >> shift
            inverse = inverses.get(level)
            if inverse is None and min(base.bit_length(), reduced.bit_length() - base.bit_length()) > 2048:
                inverse = _reciprocal(base)
                inverses[level] = inverse
            high, low = _positive(reduced, base, inverse)
            low = (low << shift) + current - (reduced << shift)
            stack.append((low, level - 1))
            stack.append((high, level - 1))
    return ("-" if negative else "") + "".join(output)


def divide_decimal(first, second):
    """符号付き10進文字列の商・余りを、10進文字列2つで返す。"""
    if max(len(first), len(second)) <= 512:
        quotient, remainder = divmod_int(_parse(first, 10, []), _parse(second, 10, []))
        return str(quotient), str(remainder)
    powers = [10 ** 512]
    quotient, remainder = divmod_int(_parse(first, 10, powers), _parse(second, 10, powers))
    inverses = {}
    return _decimal(quotient, powers, inverses), _decimal(remainder, powers, inverses)


def divide_hex(first, second):
    """符号付き16進文字列の商・余りを、大文字の16進文字列2つで返す。"""
    quotient, remainder = divmod_int(_parse(first, 16, None), _parse(second, 16, None))
    return format(quotient, "X"), format(remainder, "X")

