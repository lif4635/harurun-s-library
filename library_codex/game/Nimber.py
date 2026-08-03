def _build_product8():
    table = [[0] * 256 for _ in range(256)]
    table[1][1] = 1
    for exponent in range(1, 4):
        bits = 1 << exponent
        half = bits >> 1
        limit = 1 << bits
        lower_limit = 1 << half
        for first in range(limit):
            for second in range(first, limit):
                if first < lower_limit and second < lower_limit:
                    continue
                if min(first, second) <= 1:
                    value = first * second
                else:
                    first_high = first >> half
                    first_low = first & (lower_limit - 1)
                    second_high = second >> half
                    second_low = second & (lower_limit - 1)
                    upper = table[first_high][second_high]
                    lower = table[first_low][second_low]
                    mixed = table[first_high ^ first_low][second_high ^ second_low]
                    correction = table[upper][lower_limit >> 1]
                    value = ((mixed ^ lower) << half) ^ correction ^ lower
                table[first][second] = table[second][first] = value
    return table


_PRODUCT8 = _build_product8()


def nim_product16(first, second):
    first_high, first_low = first >> 8, first & 255
    second_high, second_low = second >> 8, second & 255
    lower = _PRODUCT8[first_low][second_low]
    mixed = _PRODUCT8[first_high ^ first_low][second_high ^ second_low]
    correction = _PRODUCT8[_PRODUCT8[first_high][second_high]][128]
    return ((mixed ^ lower) << 8) ^ correction ^ lower


def nim_product32(first, second):
    first_high, first_low = first >> 16, first & 65535
    second_high, second_low = second >> 16, second & 65535
    lower = nim_product16(first_low, second_low)
    mixed = nim_product16(first_high ^ first_low, second_high ^ second_low)
    correction = nim_product16(nim_product16(first_high, second_high), 1 << 15)
    return ((mixed ^ lower) << 16) ^ correction ^ lower


def nim_product64(first, second):
    mask = (1 << 32) - 1
    first_high, first_low = first >> 32, first & mask
    second_high, second_low = second >> 32, second & mask
    lower = nim_product32(first_low, second_low)
    mixed = nim_product32(first_high ^ first_low, second_high ^ second_low)
    correction = nim_product32(nim_product32(first_high, second_high), 1 << 31)
    return ((mixed ^ lower) << 32) ^ correction ^ lower


def nim_product(first, second, bits=64):
    if bits <= 8:
        return _PRODUCT8[first][second]
    if bits <= 16:
        return nim_product16(first, second)
    if bits <= 32:
        return nim_product32(first, second)
    if bits <= 64:
        return nim_product64(first, second)
    raise ValueError("only nimbers up to 64 bits are supported")


class Nimber:
    __slots__ = ("value", "bits")

    def __init__(self, value=0, bits=64):
        if bits not in (8, 16, 32, 64):
            raise ValueError("bits must be 8, 16, 32, or 64")
        self.bits = bits
        self.value = value & ((1 << bits) - 1)

    x = property(lambda self: self.value)
    v = property(lambda self: self.value)

    def _coerce(self, other):
        if isinstance(other, Nimber):
            if self.bits != other.bits:
                raise ValueError("nimber widths differ")
            return other.value
        return other

    def __int__(self):
        return self.value

    def __eq__(self, other):
        return self.value == self._coerce(other)

    def __add__(self, other):
        return Nimber(self.value ^ self._coerce(other), self.bits)

    __sub__ = __add__
    __radd__ = __add__
    __rsub__ = __add__

    def __mul__(self, other):
        return Nimber(nim_product(self.value, self._coerce(other), self.bits),
                      self.bits)

    __rmul__ = __mul__

    def power(self, exponent):
        if exponent < 0:
            raise ValueError("nimber exponent must be nonnegative")
        result = Nimber(1, self.bits)
        base = self
        while exponent:
            if exponent & 1:
                result = result * base
            exponent >>= 1
            if exponent:
                base = base * base
        return result

    pow = power

    def inverse(self):
        if self.value == 0:
            raise ZeroDivisionError("zero nimber has no inverse")
        return self.power((1 << self.bits) - 2)

    inv = inverse

    def __truediv__(self, other):
        other = Nimber(self._coerce(other), self.bits)
        return self * other.inverse()


class NimberToField:
    """Linear basis conversion between nimber bits and a polynomial basis."""

    __slots__ = ("bits", "field_to_nimber", "nimber_to_field")

    def __init__(self, primitive_root):
        if not isinstance(primitive_root, Nimber):
            primitive_root = Nimber(primitive_root)
        bits = primitive_root.bits
        self.bits = bits
        columns = [0] * bits
        current = Nimber(1, bits)
        for index in range(bits):
            columns[index] = current.value
            current = current * primitive_root
        rows = [0] * bits
        for row in range(bits):
            left = 0
            for column, value in enumerate(columns):
                if value >> row & 1:
                    left |= 1 << column
            rows[row] = left | (1 << (bits + row))
        for column in range(bits):
            pivot = column
            while pivot < bits and (rows[pivot] >> column & 1) == 0:
                pivot += 1
            if pivot == bits:
                raise ValueError("primitive_root powers do not form a basis")
            rows[column], rows[pivot] = rows[pivot], rows[column]
            for row in range(bits):
                if row != column and (rows[row] >> column & 1):
                    rows[row] ^= rows[column]
        inverse_rows = [row >> bits for row in rows]
        reverse_columns = [0] * bits
        for input_bit in range(bits):
            coordinate = 0
            for output_bit, row in enumerate(inverse_rows):
                if row >> input_bit & 1:
                    coordinate |= 1 << output_bit
            reverse_columns[input_bit] = coordinate
        self.field_to_nimber = columns
        self.nimber_to_field = reverse_columns

    @staticmethod
    def _apply(columns, value):
        result = 0
        while value:
            bit = (value & -value).bit_length() - 1
            result ^= columns[bit]
            value &= value - 1
        return result

    def field2nimber(self, value):
        return Nimber(self._apply(self.field_to_nimber, value), self.bits)

    def nimber2field(self, value):
        if isinstance(value, Nimber):
            value = value.value
        return self._apply(self.nimber_to_field, value)


Nimber8 = lambda value=0: Nimber(value, 8)
Nimber16 = lambda value=0: Nimber(value, 16)
Nimber32 = lambda value=0: Nimber(value, 32)
Nimber64 = lambda value=0: Nimber(value, 64)
product16 = nim_product16
product32 = nim_product32
product64 = nim_product64
