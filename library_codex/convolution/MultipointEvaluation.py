from library_codex.convolution.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_derivative,
    fps_multiply,
    fps_remainder,
    fps_shrink,
)


def _batch_inverse(values, mod):
    size = len(values)
    prefix = [1] * (size + 1)
    for index, value in enumerate(values):
        value %= mod
        if value == 0:
            raise ValueError("interpolation points must be distinct modulo mod")
        prefix[index + 1] = prefix[index] * value % mod
    try:
        inverse = pow(prefix[-1], -1, mod)
    except ValueError as error:
        raise ZeroDivisionError("interpolation requires a field") from error
    result = [0] * size
    for index in range(size - 1, -1, -1):
        result[index] = inverse * prefix[index] % mod
        inverse = inverse * (values[index] % mod) % mod
    return result


class ProductTree:
    __slots__ = ("points", "mod", "n", "size", "products")

    def __init__(self, points, mod=DEFAULT_MOD):
        self.mod = mod
        self.points = [value % mod for value in points]
        self.n = len(self.points)
        size = 1
        while size < self.n:
            size <<= 1
        self.size = size
        products = [None] * (size << 1)
        for index, value in enumerate(self.points):
            products[size + index] = [-value % mod, 1]
        for node in range(size - 1, 0, -1):
            left = products[node << 1]
            right = products[node << 1 | 1]
            if left is None:
                products[node] = right
            elif right is None:
                products[node] = left
            else:
                products[node] = fps_multiply(left, right, mod)
        self.products = products

    @property
    def polynomial(self):
        if self.n == 0:
            return [1]
        return self.products[1][:]

    def evaluate(self, polynomial, direct_threshold=64):
        if direct_threshold < 1:
            raise ValueError("direct_threshold must be positive")
        if self.n == 0:
            return []
        mod = self.mod
        current = fps_shrink(polynomial, mod)
        if not current:
            return [0] * self.n
        root = self.products[1]
        if len(current) >= len(root):
            current = fps_remainder(current, root, mod)
            if not current:
                return [0] * self.n
        result = [0] * self.n
        stack = [(1, 0, self.size, current)]
        points = self.points
        products = self.products
        limit = self.n
        while stack:
            node, left, right, values = stack.pop()
            active_right = min(right, limit)
            if left >= active_right:
                continue
            if (
                active_right - left <= direct_threshold
                or len(values) <= direct_threshold
            ):
                for point_index in range(left, active_right):
                    value = 0
                    point = points[point_index]
                    for coefficient in reversed(values):
                        value = (value * point + coefficient) % mod
                    result[point_index] = value
                continue
            middle = (left + right) >> 1
            right_node = node << 1 | 1
            right_product = products[right_node]
            if right_product is not None and middle < limit:
                if len(values) < len(right_product):
                    right_values = values
                else:
                    right_values = fps_remainder(values, right_product, mod)
                stack.append((right_node, middle, right, right_values))
            left_node = node << 1
            left_product = products[left_node]
            if len(values) < len(left_product):
                left_values = values
            else:
                left_values = fps_remainder(values, left_product, mod)
            stack.append((left_node, left, middle, left_values))
        return result

    def interpolate(self, values):
        if len(values) != self.n:
            raise ValueError("points and values must have the same length")
        if self.n == 0:
            return []
        mod = self.mod
        derivative_values = self.evaluate(fps_derivative(self.products[1], mod))
        inverse_values = _batch_inverse(derivative_values, mod)
        coefficients = [None] * (self.size << 1)
        for index, value in enumerate(values):
            coefficients[self.size + index] = [
                value * inverse_values[index] % mod
            ]
        products = self.products
        for node in range(self.size - 1, 0, -1):
            left_node = node << 1
            right_node = left_node | 1
            left = coefficients[left_node]
            right = coefficients[right_node]
            if left is None:
                coefficients[node] = right
            elif right is None:
                coefficients[node] = left
            else:
                coefficients[node] = fps_add(
                    fps_multiply(left, products[right_node], mod),
                    fps_multiply(right, products[left_node], mod),
                    mod,
                )
        result = coefficients[1]
        result.extend([0] * (self.n - len(result)))
        return result[:self.n]


def multipoint_evaluation(polynomial, points, mod=DEFAULT_MOD):
    return ProductTree(points, mod).evaluate(polynomial)


def polynomial_interpolation(points, values, mod=DEFAULT_MOD):
    return ProductTree(points, mod).interpolate(values)


def interpolate_consecutive(values, point, mod=DEFAULT_MOD):
    size = len(values)
    if size == 0:
        raise ValueError("at least one value is required")
    if size > mod:
        raise ValueError("the number of points must not exceed mod")
    point %= mod
    if point < size:
        return values[point] % mod
    left = [1] * (size + 1)
    right = [1] * (size + 1)
    for index in range(size):
        left[index + 1] = left[index] * (point - index) % mod
    for index in range(size - 1, -1, -1):
        right[index] = right[index + 1] * (point - index) % mod
    factorial = 1
    for index in range(2, size):
        factorial = factorial * index % mod
    try:
        inverse_factorial = pow(factorial, -1, mod)
    except ValueError as error:
        raise ZeroDivisionError("interpolation requires a field") from error
    inverse_factorials = [1] * size
    if size > 1:
        inverse_factorials[-1] = inverse_factorial
        for index in range(size - 1, 0, -1):
            inverse_factorials[index - 1] = (
                inverse_factorials[index] * index % mod
            )
    result = 0
    last = size - 1
    for index, value in enumerate(values):
        term = (
            value
            * left[index]
            * right[index + 1]
            * inverse_factorials[index]
            * inverse_factorials[last - index]
        ) % mod
        if (last - index) & 1:
            result -= term
        else:
            result += term
    return result % mod


def _sample_point_shift_segment(values, point, count, mod):
    from library_codex.convolution.FormalPowerSeries import fps_multiply

    degree = len(values) - 1
    factorial = 1
    for index in range(2, degree + 1):
        factorial = factorial * index % mod
    inverse_factorial = [1] * (degree + 1)
    if degree:
        inverse_factorial[-1] = pow(factorial, -1, mod)
        for index in range(degree, 0, -1):
            inverse_factorial[index - 1] = (
                inverse_factorial[index] * index % mod
            )
    weighted = [0] * (degree + 1)
    for index, value in enumerate(values):
        weighted[index] = (
            value
            * inverse_factorial[index]
            * inverse_factorial[degree - index]
        ) % mod
        if (degree - index) & 1:
            weighted[index] = -weighted[index] % mod
    reciprocals = [0] * (count + degree)
    for index in range(len(reciprocals)):
        reciprocals[index] = pow(point - degree + index, -1, mod)
    product = fps_multiply(weighted, reciprocals, mod)
    falling = point % mod
    for index in range(1, degree + 1):
        falling = falling * (point - index) % mod
    result = [0] * count
    for index in range(count):
        result[index] = falling * product[degree + index] % mod
        falling = falling * (point + index + 1) % mod
        falling = falling * reciprocals[index] % mod
    return result


def sample_point_shift(values, point, count=None, mod=DEFAULT_MOD):
    if not values:
        raise ValueError("at least one sample is required")
    if count is None:
        count = len(values)
    if count < 0:
        raise ValueError("count must be nonnegative")
    if len(values) > mod:
        raise ValueError("the number of samples must not exceed mod")
    if count == 0:
        return []
    degree = len(values) - 1
    current = point % mod
    remaining = count
    result = []
    while remaining:
        segment = min(remaining, mod - current)
        if current <= degree:
            copied = min(segment, degree - current + 1)
            result.extend(
                value % mod for value in values[current:current + copied]
            )
            current += copied
            remaining -= copied
            segment -= copied
            if remaining == 0:
                break
            if current == mod:
                current = 0
                continue
        if segment:
            result.extend(
                _sample_point_shift_segment(
                    values, current, segment, mod
                )
            )
            current += segment
            remaining -= segment
        if current == mod:
            current = 0
    return result


MultipointEvaluation = multipoint_evaluation
PolynomialInterpolation = polynomial_interpolation
Interpolate = interpolate_consecutive
SamplePointShift = sample_point_shift
