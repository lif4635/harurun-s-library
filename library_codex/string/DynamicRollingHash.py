from library_codex.string.RollingHash import (
    DEFAULT_BASE,
    HashString,
    MOD,
    _fma,
    _mul,
    _symbol_value,
)


class DynamicRollingHash:
    __slots__ = (
        "n", "size", "base", "data", "power", "forward", "reverse",
        "length",
    )

    def __init__(self, sequence=(), base=DEFAULT_BASE):
        sequence = list(sequence)
        n = len(sequence)
        size = 1
        while size < n:
            size <<= 1
        power = [1] * (n + 1)
        for i in range(n):
            power[i + 1] = _mul(power[i], base)
        forward = [0] * (size << 1)
        reverse = [0] * (size << 1)
        length = [0] * (size << 1)
        for i, symbol in enumerate(sequence):
            value = _symbol_value(symbol)
            position = size + i
            forward[position] = reverse[position] = value
            length[position] = 1
        for position in range(size - 1, 0, -1):
            left = position << 1
            right = left | 1
            left_length = length[left]
            right_length = length[right]
            length[position] = left_length + right_length
            forward[position] = _fma(
                forward[left], power[right_length], forward[right]
            )
            reverse[position] = _fma(
                reverse[right], power[left_length], reverse[left]
            )
        self.n = n
        self.size = size
        self.base = base
        self.data = sequence
        self.power = power
        self.forward = forward
        self.reverse = reverse
        self.length = length

    def __len__(self):
        return self.n

    def update(self, index, value):
        assert 0 <= index < self.n
        self.data[index] = value
        position = self.size + index
        value = _symbol_value(value)
        self.forward[position] = self.reverse[position] = value
        position >>= 1
        while position:
            left = position << 1
            right = left | 1
            left_length = self.length[left]
            right_length = self.length[right]
            self.forward[position] = _fma(
                self.forward[left], self.power[right_length],
                self.forward[right],
            )
            self.reverse[position] = _fma(
                self.reverse[right], self.power[left_length],
                self.reverse[left],
            )
            position >>= 1

    set = update

    def _query(self, left, right):
        assert 0 <= left <= right <= self.n
        left += self.size
        right += self.size
        left_forward = left_reverse = left_length = 0
        right_forward = right_reverse = right_length = 0
        while left < right:
            if left & 1:
                node_length = self.length[left]
                left_forward = _fma(
                    left_forward, self.power[node_length],
                    self.forward[left],
                )
                left_reverse = _fma(
                    self.reverse[left], self.power[left_length],
                    left_reverse,
                )
                left_length += node_length
                left += 1
            if right & 1:
                right -= 1
                node_length = self.length[right]
                right_forward = _fma(
                    self.forward[right], self.power[right_length],
                    right_forward,
                )
                right_reverse = _fma(
                    right_reverse, self.power[node_length],
                    self.reverse[right],
                )
                right_length += node_length
            left >>= 1
            right >>= 1
        forward = _fma(
            left_forward, self.power[right_length], right_forward
        )
        reverse = _fma(
            right_reverse, self.power[left_length], left_reverse
        )
        return forward, reverse, left_length + right_length

    def get(self, left=0, right=None):
        if right is None:
            right = self.n
        return self._query(left, right)[0]

    query = get

    def reverse_get(self, left=0, right=None):
        if right is None:
            right = self.n
        return self._query(left, right)[1]

    def get_value(self, left=0, right=None):
        if right is None:
            right = self.n
        forward, reverse, length = self._query(left, right)
        return HashString(
            forward, self.power[length], length, (self.base,), reverse
        )

    def same(self, left1, right1, left2, right2):
        return (
            right1 - left1 == right2 - left2
            and self.get(left1, right1) == self.get(left2, right2)
        )

    def is_palindrome(self, left=0, right=None):
        if right is None:
            right = self.n
        forward, reverse, _ = self._query(left, right)
        return forward == reverse

    def lcp(self, left1, right1, left2, right2):
        length = min(right1 - left1, right2 - left2)
        low = 0
        high = length + 1
        while high - low > 1:
            middle = (low + high) >> 1
            if self.get(left1, left1 + middle) == self.get(
                left2, left2 + middle
            ):
                low = middle
            else:
                high = middle
        return low

    def __getitem__(self, index):
        return self.data[index]
