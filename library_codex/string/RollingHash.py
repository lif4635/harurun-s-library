from time import time_ns


MOD = (1 << 61) - 1
MASK = MOD


def _mul(left, right):
    value = left * right
    value = (value & MASK) + (value >> 61)
    return value - MOD if value >= MOD else value


def _fma(left, right, add):
    value = left * right + add
    value = (value & MASK) + (value >> 61)
    return value - MOD if value >= MOD else value


def _splitmix(value):
    value = (value + 0x9E3779B97F4A7C15) & ((1 << 64) - 1)
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & ((1 << 64) - 1)
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & ((1 << 64) - 1)
    return value ^ (value >> 31)


_seed = time_ns() ^ id(object())
DEFAULT_BASE = _splitmix(_seed) % (MOD - (1 << 20)) + (1 << 20)
DEFAULT_BASE2 = _splitmix(_seed ^ 0xD1B54A32D192ED03) % (MOD - (1 << 20)) + (1 << 20)
if DEFAULT_BASE2 == DEFAULT_BASE:
    DEFAULT_BASE2 -= 1


def _symbol_value(symbol):
    if isinstance(symbol, str):
        symbol = ord(symbol)
    return int(symbol) % MOD


def _component_hash(sequence, base):
    value = 0
    for symbol in sequence:
        value = _fma(value, base, _symbol_value(symbol))
    return value


def hash_sequence(sequence, base=DEFAULT_BASE, base2=None):
    first = _component_hash(sequence, base)
    if base2 is None:
        return first
    return first, _component_hash(sequence, base2)


def _combine_hash(left, right, right_power):
    if isinstance(left, tuple):
        return tuple(
            _fma(a, p, b) for a, b, p in zip(left, right, right_power)
        )
    return _fma(left, right_power, right)


def _multiply_hash(left, right):
    if isinstance(left, tuple):
        return tuple(_mul(a, b) for a, b in zip(left, right))
    return _mul(left, right)


class HashString:
    __slots__ = ("hash", "reverse_hash", "power", "length", "bases")

    def __init__(self, value, power, length, bases, reverse_value=None):
        self.hash = value
        self.reverse_hash = reverse_value
        self.power = power
        self.length = length
        self.bases = bases

    @classmethod
    def empty(cls, bases=(DEFAULT_BASE,), reversible=False):
        if len(bases) == 1:
            return cls(0, 1, 0, bases, 0 if reversible else None)
        zero = (0,) * len(bases)
        one = (1,) * len(bases)
        return cls(zero, one, 0, bases, zero if reversible else None)

    @classmethod
    def from_sequence(cls, sequence, base=DEFAULT_BASE, base2=None, reversible=False):
        rolling = RollingHash(sequence, base, base2, reversible)
        return rolling.get_value(0, len(rolling))

    def __len__(self):
        return self.length

    def __eq__(self, other):
        return (
            isinstance(other, HashString)
            and self.length == other.length
            and self.bases == other.bases
            and self.hash == other.hash
        )

    def __hash__(self):
        return hash((self.length, self.bases, self.hash))

    def __add__(self, other):
        if not isinstance(other, HashString) or self.bases != other.bases:
            return NotImplemented
        value = _combine_hash(self.hash, other.hash, other.power)
        power = _multiply_hash(self.power, other.power)
        if self.reverse_hash is None or other.reverse_hash is None:
            reverse_value = None
        else:
            reverse_value = _combine_hash(
                other.reverse_hash, self.reverse_hash, self.power
            )
        return HashString(
            value, power, self.length + other.length, self.bases, reverse_value
        )

    concat = __add__

    def reversed(self):
        if self.reverse_hash is None:
            raise ValueError("reverse hash was not built")
        return HashString(
            self.reverse_hash, self.power, self.length, self.bases, self.hash
        )

    reverse = reversed

    def is_palindrome(self):
        return self.reverse_hash is not None and self.hash == self.reverse_hash

    def repeat(self, count):
        assert count >= 0
        result = HashString.empty(
            self.bases, self.reverse_hash is not None
        )
        block = self
        while count:
            if count & 1:
                result = result + block
            count >>= 1
            if count:
                block = block + block
        return result

    def __mul__(self, count):
        return self.repeat(count)

    __rmul__ = __mul__

    def remove_prefix(self, prefix):
        assert self.bases == prefix.bases and prefix.length <= self.length
        remaining = self.length - prefix.length
        if len(self.bases) == 1:
            power = pow(self.bases[0], remaining, MOD)
            value = self.hash - _mul(prefix.hash, power)
            if value < 0:
                value += MOD
        else:
            power = tuple(pow(base, remaining, MOD) for base in self.bases)
            value = []
            for full, part, component_power in zip(self.hash, prefix.hash, power):
                current = full - _mul(part, component_power)
                value.append(current + MOD if current < 0 else current)
            value = tuple(value)
        return HashString(value, power, remaining, self.bases)


class RollingHash:
    __slots__ = (
        "data", "n", "base", "base2", "prefix", "power", "prefix2",
        "power2", "reverse_prefix", "reverse_prefix2", "reversible",
    )

    def __init__(self, sequence=(), base=DEFAULT_BASE, base2=None, reversible=False):
        if not hasattr(sequence, "__len__"):
            sequence = list(sequence)
        self.data = sequence
        self.n = len(sequence)
        self.base = base
        self.base2 = base2
        self.reversible = reversible
        prefix = [0] * (self.n + 1)
        power = [1] * (self.n + 1)
        value = 0
        base_power = 1
        for i, symbol in enumerate(sequence):
            value = _fma(value, base, _symbol_value(symbol))
            base_power = _mul(base_power, base)
            prefix[i + 1] = value
            power[i + 1] = base_power
        self.prefix = prefix
        self.power = power

        if base2 is None:
            self.prefix2 = None
            self.power2 = None
        else:
            prefix2 = [0] * (self.n + 1)
            power2 = [1] * (self.n + 1)
            value = 0
            base_power = 1
            for i, symbol in enumerate(sequence):
                value = _fma(value, base2, _symbol_value(symbol))
                base_power = _mul(base_power, base2)
                prefix2[i + 1] = value
                power2[i + 1] = base_power
            self.prefix2 = prefix2
            self.power2 = power2

        if reversible:
            reverse_prefix = [0] * (self.n + 1)
            value = 0
            for i in range(self.n):
                value = _fma(
                    value, base, _symbol_value(sequence[self.n - 1 - i])
                )
                reverse_prefix[i + 1] = value
            self.reverse_prefix = reverse_prefix
            if base2 is None:
                self.reverse_prefix2 = None
            else:
                reverse_prefix2 = [0] * (self.n + 1)
                value = 0
                for i in range(self.n):
                    value = _fma(
                        value, base2,
                        _symbol_value(sequence[self.n - 1 - i]),
                    )
                    reverse_prefix2[i + 1] = value
                self.reverse_prefix2 = reverse_prefix2
        else:
            self.reverse_prefix = None
            self.reverse_prefix2 = None

    def __len__(self):
        return self.n

    @property
    def bases(self):
        return (self.base,) if self.base2 is None else (self.base, self.base2)

    def _get_component(self, prefix, power, left, right):
        value = prefix[right] - _mul(prefix[left], power[right - left])
        return value + MOD if value < 0 else value

    def get(self, left=0, right=None):
        if right is None:
            right = self.n
        assert 0 <= left <= right <= self.n
        first = self._get_component(self.prefix, self.power, left, right)
        if self.base2 is None:
            return first
        return first, self._get_component(
            self.prefix2, self.power2, left, right
        )

    query = get

    def reverse_get(self, left=0, right=None):
        if right is None:
            right = self.n
        if self.reverse_prefix is None:
            raise ValueError("reverse hash was not built")
        assert 0 <= left <= right <= self.n
        reverse_left = self.n - right
        reverse_right = self.n - left
        first = self._get_component(
            self.reverse_prefix, self.power, reverse_left, reverse_right
        )
        if self.base2 is None:
            return first
        return first, self._get_component(
            self.reverse_prefix2, self.power2, reverse_left, reverse_right
        )

    def get_value(self, left=0, right=None):
        if right is None:
            right = self.n
        length = right - left
        if self.base2 is None:
            power = self.power[length]
        else:
            power = self.power[length], self.power2[length]
        reverse_value = (
            self.reverse_get(left, right) if self.reversible else None
        )
        return HashString(
            self.get(left, right), power, length, self.bases, reverse_value
        )

    to_hash_string = get_value

    def same(self, left1, right1, other, left2, right2):
        return (
            right1 - left1 == right2 - left2
            and self.bases == other.bases
            and self.get(left1, right1) == other.get(left2, right2)
        )

    def lcp(self, other, left1=0, right1=None, left2=0, right2=None):
        if right1 is None:
            right1 = self.n
        if right2 is None:
            right2 = other.n
        assert self.bases == other.bases
        length = min(right1 - left1, right2 - left2)
        low = 0
        high = length + 1
        while high - low > 1:
            middle = (low + high) >> 1
            if self.get(left1, left1 + middle) == other.get(
                left2, left2 + middle
            ):
                low = middle
            else:
                high = middle
        return low

    LCP = lcp

    def compare(self, other, left1=0, right1=None, left2=0, right2=None):
        if right1 is None:
            right1 = self.n
        if right2 is None:
            right2 = other.n
        common = self.lcp(other, left1, right1, left2, right2)
        end1 = left1 + common == right1
        end2 = left2 + common == right2
        if end1:
            return 0 if end2 else -1
        if end2:
            return 1
        return -1 if self.data[left1 + common] < other.data[left2 + common] else 1

    strcmp = compare

    def find(self, pattern, lower=0):
        if isinstance(pattern, RollingHash):
            target = pattern.get()
            length = pattern.n
            assert self.bases == pattern.bases
        else:
            length = len(pattern)
            target = hash_sequence(pattern, self.base, self.base2)
        for i in range(lower, self.n - length + 1):
            if self.get(i, i + length) == target:
                return i
        return -1

    def append(self, symbol):
        if self.reversible:
            raise ValueError("incremental append is unavailable with reverse hash")
        if not isinstance(self.data, list):
            self.data = list(self.data)
        self.data.append(symbol)
        value = _symbol_value(symbol)
        self.prefix.append(_fma(self.prefix[-1], self.base, value))
        self.power.append(_mul(self.power[-1], self.base))
        if self.base2 is not None:
            self.prefix2.append(_fma(self.prefix2[-1], self.base2, value))
            self.power2.append(_mul(self.power2[-1], self.base2))
        self.n += 1

    def extend(self, sequence):
        for symbol in sequence:
            self.append(symbol)
        return self

    connect = extend

    def __getitem__(self, index):
        if isinstance(index, slice):
            left, right, step = index.indices(self.n)
            if step != 1:
                return self.data[index]
            return RollingHashView(self, left, right)
        return self.data[index]


class DoubleRollingHash(RollingHash):
    __slots__ = ()

    def __init__(self, sequence=(), bases=None, reversible=False):
        if bases is None:
            bases = DEFAULT_BASE, DEFAULT_BASE2
        super().__init__(sequence, bases[0], bases[1], reversible)


class ReversibleRollingHash(RollingHash):
    __slots__ = ()

    def __init__(self, sequence=(), base=DEFAULT_BASE, base2=None):
        super().__init__(sequence, base, base2, True)


class RollingHashView:
    __slots__ = ("base", "left", "right", "l", "r")

    def __init__(self, base, left, right):
        self.base = base
        self.left = left
        self.right = right
        self.l = left
        self.r = right

    def __len__(self):
        return self.right - self.left

    @property
    def hash(self):
        return self.base.get(self.left, self.right)

    def to_hash_string(self):
        return self.base.get_value(self.left, self.right)

    def lcp(self, other):
        return self.base.lcp(
            other.base, self.left, self.right, other.left, other.right
        )

    LCP = lcp

    def compare(self, other):
        return self.base.compare(
            other.base, self.left, self.right, other.left, other.right
        )

    cmp = compare

    def is_palindrome(self):
        return self.to_hash_string().is_palindrome()

    def reversed(self):
        return self.to_hash_string().reversed()

    def __getitem__(self, index):
        if isinstance(index, slice):
            left, right, step = index.indices(len(self))
            if step != 1:
                return self.base.data[self.left:self.right][index]
            return RollingHashView(
                self.base, self.left + left, self.left + right
            )
        if index < 0:
            index += len(self)
        if not 0 <= index < len(self):
            raise IndexError("rolling hash view index out of range")
        return self.base.data[self.left + index]

    def __eq__(self, other):
        return (
            isinstance(other, RollingHashView)
            and len(self) == len(other)
            and self.base.bases == other.base.bases
            and self.hash == other.hash
        )

    def __lt__(self, other):
        return self.compare(other) < 0

    def __str__(self):
        return str(self.base.data[self.left:self.right])
