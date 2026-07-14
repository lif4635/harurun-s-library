from library_codex.convolution.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_exponential,
    fps_integral,
    fps_inverse,
    fps_multiply,
    fps_negate,
    fps_subtract,
)


class RelaxedConvolution:
    """Online convolution: append a[n], b[n] and obtain coefficient n."""

    __slots__ = ("limit", "mod", "position", "first", "second", "result")

    def __init__(self, limit, mod=DEFAULT_MOD):
        if limit < 0:
            raise ValueError("limit must be nonnegative")
        self.limit = limit
        self.mod = mod
        self.position = 0
        self.first = [0] * limit
        self.second = [0] * limit
        self.result = [0] * limit

    def next(self, first, second):
        position = self.position
        if position >= self.limit:
            raise IndexError("relaxed convolution limit exceeded")
        mod = self.mod
        first %= mod
        second %= mod
        self.first[position] = first
        self.second[position] = second
        self.result[position] = (
            self.result[position]
            + first * self.second[0]
            + (second * self.first[0] if position else 0)
        ) % mod
        self.position += 1
        q = self.position
        if q >= self.limit:
            return self.result[position]
        block = 1
        while block <= q:
            if q % (block << 1) == block:
                if q == block:
                    product = fps_multiply(
                        self.first[:block], self.second[:block], mod
                    )
                else:
                    left = fps_multiply(
                        self.first[q - block:q], self.second[:block << 1], mod
                    )
                    right = fps_multiply(
                        self.second[q - block:q], self.first[:block << 1], mod
                    )
                    size = max(len(left), len(right))
                    product = [0] * size
                    for index in range(size):
                        product[index] = (
                            (left[index] if index < len(left) else 0)
                            + (right[index] if index < len(right) else 0)
                        ) % mod
                end = min(q + block, self.limit)
                for index in range(q, end):
                    source = block + index - q
                    if source < len(product):
                        self.result[index] = (
                            self.result[index] + product[source]
                        ) % mod
            block <<= 1
        return self.result[position]

    get = next


class RelaxedInverse:
    __slots__ = ("limit", "mod", "position", "values", "convolution")

    def __init__(self, limit, mod=DEFAULT_MOD):
        self.limit = limit
        self.mod = mod
        self.position = 0
        self.values = [0] * limit
        self.convolution = RelaxedConvolution(max(0, limit - 1), mod)

    def next(self, value):
        position = self.position
        if position == 0:
            self.values[0] = pow(value % self.mod, -1, self.mod)
        else:
            coefficient = self.convolution.next(value, self.values[position - 1])
            self.values[position] = -self.values[0] * coefficient % self.mod
        self.position += 1
        return self.values[position]

    def __getitem__(self, index):
        return self.values[index]


class RelaxedExponential:
    __slots__ = ("limit", "mod", "position", "values", "convolution")

    def __init__(self, limit, mod=DEFAULT_MOD):
        self.limit = limit
        self.mod = mod
        self.position = 0
        self.values = [0] * limit
        self.convolution = RelaxedConvolution(max(0, limit - 1), mod)

    def next(self, value):
        position = self.position
        if position == 0:
            if value % self.mod:
                raise ValueError("exponential requires constant coefficient zero")
            self.values[0] = 1
        else:
            coefficient = self.convolution.next(
                value * position % self.mod, self.values[position - 1]
            )
            self.values[position] = coefficient * pow(position, -1, self.mod) % self.mod
        self.position += 1
        return self.values[position]

    def __getitem__(self, index):
        return self.values[index]


class RelaxedLogarithm:
    __slots__ = ("limit", "mod", "position", "values", "inverse",
                 "convolution")

    def __init__(self, limit, mod=DEFAULT_MOD):
        self.limit = limit
        self.mod = mod
        self.position = 0
        self.values = [0] * limit
        self.inverse = RelaxedInverse(limit, mod)
        self.convolution = RelaxedConvolution(max(0, limit - 1), mod)

    def next(self, value):
        position = self.position
        self.inverse.next(value)
        if position == 0:
            if value % self.mod != 1:
                raise ValueError("logarithm requires constant coefficient one")
            self.values[0] = 0
        else:
            coefficient = self.convolution.next(
                value * position % self.mod, self.inverse[position - 1]
            )
            self.values[position] = coefficient * pow(position, -1, self.mod) % self.mod
        self.position += 1
        return self.values[position]

    def __getitem__(self, index):
        return self.values[index]


class OnlineFormalPowerSeries:
    """Lazy coefficient stream supporting algebra and self-referential definitions."""

    __slots__ = ("mod", "values", "function", "computing")

    def __init__(self, series=None, function=None, mod=DEFAULT_MOD):
        self.mod = mod
        self.values = [value % mod for value in (series or ())]
        self.function = function or (lambda _index: 0)
        self.computing = False

    def set_corner(self, series):
        self.values = [value % self.mod for value in series]
        return self

    def set_function(self, function):
        self.function = function
        return self

    def set(self, other):
        self.function = lambda index: other[index]
        return self

    def get(self, index):
        if index < 0:
            return 0
        while len(self.values) <= index:
            if self.computing:
                raise ValueError("online FPS dependency requests an unconfirmed coefficient")
            self.computing = True
            try:
                value = self.function(len(self.values)) % self.mod
            finally:
                self.computing = False
            self.values.append(value)
        return self.values[index]

    __getitem__ = get

    def prefix(self, size):
        if size <= 0:
            return []
        self.get(size - 1)
        return self.values[:size]

    pre = prefix

    @staticmethod
    def _coerce(value, mod):
        return value if isinstance(value, OnlineFormalPowerSeries) else (
            OnlineFormalPowerSeries([value], mod=mod)
        )

    def __add__(self, other):
        other = self._coerce(other, self.mod)
        return OnlineFormalPowerSeries(
            function=lambda index: self[index] + other[index], mod=self.mod
        )

    __radd__ = __add__

    def __sub__(self, other):
        other = self._coerce(other, self.mod)
        return OnlineFormalPowerSeries(
            function=lambda index: self[index] - other[index], mod=self.mod
        )

    def __rsub__(self, other):
        return self._coerce(other, self.mod) - self

    def __neg__(self):
        return OnlineFormalPowerSeries(
            function=lambda index: -self[index], mod=self.mod
        )

    def scale(self, scalar):
        return OnlineFormalPowerSeries(
            function=lambda index: self[index] * scalar, mod=self.mod
        )

    def __mul__(self, other):
        if not isinstance(other, OnlineFormalPowerSeries):
            return self.scale(other)
        limit = [1]
        convolution = [RelaxedConvolution(1, self.mod)]

        def coefficient(index):
            if index >= limit[0]:
                new_limit = 1
                while new_limit <= index:
                    new_limit <<= 1
                old_count = convolution[0].position
                rebuilt = RelaxedConvolution(new_limit, self.mod)
                for old in range(old_count):
                    rebuilt.next(self[old], other[old])
                convolution[0] = rebuilt
                limit[0] = new_limit
            while convolution[0].position <= index:
                position = convolution[0].position
                value = convolution[0].next(self[position], other[position])
            return convolution[0].result[index]

        return OnlineFormalPowerSeries(function=coefficient, mod=self.mod)

    __rmul__ = __mul__

    def shift_left(self, amount):
        return OnlineFormalPowerSeries(
            function=lambda index: 0 if index < amount else self[index - amount],
            mod=self.mod,
        )

    def shift_right(self, amount):
        return OnlineFormalPowerSeries(
            function=lambda index: self[index + amount], mod=self.mod
        )

    def derivative(self):
        return OnlineFormalPowerSeries(
            function=lambda index: (index + 1) * self[index + 1], mod=self.mod
        )

    diff = derivative

    def integral(self):
        return OnlineFormalPowerSeries(
            function=lambda index: 0 if index == 0 else self[index - 1]
            * pow(index, -1, self.mod), mod=self.mod
        )

    def inverse(self):
        relaxed = [RelaxedInverse(1, self.mod)]
        limit = [1]

        def coefficient(index):
            if index >= limit[0]:
                new_limit = 1
                while new_limit <= index:
                    new_limit <<= 1
                rebuilt = RelaxedInverse(new_limit, self.mod)
                for old in range(relaxed[0].position):
                    rebuilt.next(self[old])
                relaxed[0] = rebuilt
                limit[0] = new_limit
            while relaxed[0].position <= index:
                relaxed[0].next(self[relaxed[0].position])
            return relaxed[0][index]

        return OnlineFormalPowerSeries(function=coefficient, mod=self.mod)

    inv = inverse

    def exponential(self):
        relaxed = [RelaxedExponential(1, self.mod)]
        limit = [1]

        def coefficient(index):
            if index >= limit[0]:
                new_limit = 1
                while new_limit <= index:
                    new_limit <<= 1
                rebuilt = RelaxedExponential(new_limit, self.mod)
                for old in range(relaxed[0].position):
                    rebuilt.next(self[old])
                relaxed[0] = rebuilt
                limit[0] = new_limit
            while relaxed[0].position <= index:
                relaxed[0].next(self[relaxed[0].position])
            return relaxed[0][index]

        return OnlineFormalPowerSeries(function=coefficient, mod=self.mod)

    exp = exponential

    def logarithm(self):
        return (self.derivative() * self.inverse()).integral()

    log = logarithm


def differential_equation(function, derivative, initial, degree, mod=DEFAULT_MOD):
    """Solve f' = function(f), with function/derivative returning truncated FPS."""
    result = [initial % mod]
    size = 1
    while size < degree:
        target = min(size << 1, degree)
        prime = derivative(result, target)
        integrating_factor = fps_exponential(
            fps_integral(fps_negate(prime, mod), mod), target, mod
        )
        value = function(result, target)
        product = fps_multiply(prime, result, mod)
        right = fps_subtract(value, product, mod)
        integrated = fps_integral(
            fps_multiply(right, integrating_factor, mod)[:target - 1], mod
        )
        if not integrated:
            integrated = [0]
        integrated[0] = (integrated[0] + initial) % mod
        result = fps_multiply(
            integrated, fps_inverse(integrating_factor, target, mod), mod
        )[:target]
        size = target
    result.extend([0] * (degree - len(result)))
    return result[:degree]


def newton_method(calculate, initial, degree, mod=DEFAULT_MOD):
    """Solve G(f)=0 by iterative precision doubling; calculate -> (G,dG/df)."""
    result = [initial % mod] if isinstance(initial, int) else list(initial)
    if not result:
        raise ValueError("an initial approximation is required")
    sizes = []
    current = degree
    while current > len(result):
        sizes.append(current)
        current = (current + 1) >> 1
    result = result[:current]
    for target in reversed(sizes):
        value, derivative = calculate(result, target + 10)
        offset = 0
        while offset < len(derivative) and derivative[offset] % mod == 0:
            offset += 1
        if offset > 10:
            raise ValueError("Newton derivative has excessive leading zeros")
        value = value[offset:]
        derivative = derivative[offset:]
        correction = fps_multiply(
            value, fps_inverse(derivative, target, mod), mod
        )[:target]
        result = fps_subtract(result, correction, mod)[:target]
        result.extend([0] * (target - len(result)))
    return result[:degree]


RelaxedInv = RelaxedInverse
RelaxedExp = RelaxedExponential
RelaxedLog = RelaxedLogarithm
ofps = OnlineFormalPowerSeries
DifferentialEquation = differential_equation
