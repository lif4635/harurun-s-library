from library_codex.string.RollingHash import (
    DEFAULT_BASE,
    DEFAULT_BASE2,
    MOD,
    _fma,
    _mul,
    _symbol_value,
)


class RollingHash2D:
    __slots__ = (
        "matrix", "height", "width", "row_base", "column_base",
        "row_power", "column_power", "prefix", "stride",
    )

    def __init__(self, matrix=(), row_base=DEFAULT_BASE, column_base=DEFAULT_BASE2):
        matrix = list(matrix)
        height = len(matrix)
        width = len(matrix[0]) if height else 0
        if any(len(row) != width for row in matrix):
            raise ValueError("matrix rows must have equal length")
        row_power = [1] * (height + 1)
        column_power = [1] * (width + 1)
        for i in range(height):
            row_power[i + 1] = _mul(row_power[i], row_base)
        for i in range(width):
            column_power[i + 1] = _mul(column_power[i], column_base)
        stride = width + 1
        prefix = [0] * ((height + 1) * stride)
        for i in range(1, height + 1):
            offset = i * stride
            value = 0
            row = matrix[i - 1]
            for j in range(1, width + 1):
                value = _fma(
                    value, column_base, _symbol_value(row[j - 1])
                )
                prefix[offset + j] = value
        for j in range(1, width + 1):
            value = 0
            for i in range(1, height + 1):
                index = i * stride + j
                value = _fma(value, row_base, prefix[index])
                prefix[index] = value
        self.matrix = matrix
        self.height = height
        self.width = width
        self.row_base = row_base
        self.column_base = column_base
        self.row_power = row_power
        self.column_power = column_power
        self.prefix = prefix
        self.stride = stride

    def get(self, upper, left, lower, right):
        assert 0 <= upper <= lower <= self.height
        assert 0 <= left <= right <= self.width
        stride = self.stride
        prefix = self.prefix
        row_power = self.row_power[lower - upper]
        column_power = self.column_power[right - left]
        value = prefix[lower * stride + right]
        value -= _mul(prefix[upper * stride + right], row_power)
        value -= _mul(prefix[lower * stride + left], column_power)
        value += _mul(
            _mul(prefix[upper * stride + left], row_power),
            column_power,
        )
        return value % MOD

    query = get

    def view(self, upper=0, left=0, lower=None, right=None):
        if lower is None:
            lower = self.height
        if right is None:
            right = self.width
        return RollingHash2DView(self, upper, left, lower, right)

    def same(self, rectangle1, rectangle2):
        u1, l1, d1, r1 = rectangle1
        u2, l2, d2, r2 = rectangle2
        return (
            d1 - u1 == d2 - u2
            and r1 - l1 == r2 - l2
            and self.get(u1, l1, d1, r1) == self.get(u2, l2, d2, r2)
        )

    def hash_matrix(self, matrix):
        result = RollingHash2D(
            matrix, self.row_base, self.column_base
        )
        return result.get(0, 0, result.height, result.width)

    def find(self, pattern):
        pattern = list(pattern)
        pattern_height = len(pattern)
        pattern_width = len(pattern[0]) if pattern_height else 0
        if any(len(row) != pattern_width for row in pattern):
            raise ValueError("pattern rows must have equal length")
        if pattern_height > self.height or pattern_width > self.width:
            return []
        target = self.hash_matrix(pattern)
        result = []
        for upper in range(self.height - pattern_height + 1):
            lower = upper + pattern_height
            for left in range(self.width - pattern_width + 1):
                if self.get(
                    upper, left, lower, left + pattern_width
                ) == target:
                    result.append((upper, left))
        return result

    def __getitem__(self, index):
        if isinstance(index, tuple) and len(index) == 2:
            rows, columns = index
            if isinstance(rows, slice) and isinstance(columns, slice):
                upper, lower, row_step = rows.indices(self.height)
                left, right, column_step = columns.indices(self.width)
                if row_step != 1 or column_step != 1:
                    raise ValueError("hash matrix slices require step 1")
                return self.view(upper, left, lower, right)
        return self.matrix[index]


class RollingHash2DView:
    __slots__ = ("base", "upper", "left", "lower", "right")

    def __init__(self, base, upper, left, lower, right):
        self.base = base
        self.upper = upper
        self.left = left
        self.lower = lower
        self.right = right

    @property
    def shape(self):
        return self.lower - self.upper, self.right - self.left

    @property
    def hash(self):
        return self.base.get(
            self.upper, self.left, self.lower, self.right
        )

    def __eq__(self, other):
        return (
            isinstance(other, RollingHash2DView)
            and self.shape == other.shape
            and self.base.row_base == other.base.row_base
            and self.base.column_base == other.base.column_base
            and self.hash == other.hash
        )

    def __getitem__(self, index):
        if isinstance(index, tuple):
            row, column = index
            return self.base.matrix[self.upper + row][self.left + column]
        return self.base.matrix[self.upper + index][self.left:self.right]
