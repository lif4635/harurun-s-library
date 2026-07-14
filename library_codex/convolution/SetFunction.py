DEFAULT_MOD = 998244353
_POPCOUNT_CACHE = {1: [0]}


def _check_size(size):
    if size < 1 or size & (size - 1):
        raise ValueError("length must be a positive power of two")


def _check_pair(first, second):
    if len(first) != len(second):
        raise ValueError("input lengths must be equal")
    _check_size(len(first))


def _popcounts(size):
    result = _POPCOUNT_CACHE.get(size)
    if result is None:
        result = [0] * size
        for mask in range(1, size):
            result[mask] = result[mask >> 1] + (mask & 1)
        _POPCOUNT_CACHE[size] = result
    return result


def _normalize(values, mod):
    if mod <= 0:
        raise ValueError("mod must be positive")
    for index in range(len(values)):
        values[index] %= mod


def subset_zeta_transform(values, mod=None):
    size = len(values)
    _check_size(size)
    step = 1
    if mod is None:
        while step < size:
            block = step << 1
            for start in range(0, size, block):
                upper = start + step
                for offset in range(step):
                    values[upper + offset] += values[start + offset]
            step = block
    else:
        _normalize(values, mod)
        while step < size:
            block = step << 1
            for start in range(0, size, block):
                upper = start + step
                for offset in range(step):
                    index = upper + offset
                    values[index] = (
                        values[index] + values[start + offset]
                    ) % mod
            step = block
    return values


def subset_mobius_transform(values, mod=None):
    size = len(values)
    _check_size(size)
    step = 1
    if mod is None:
        while step < size:
            block = step << 1
            for start in range(0, size, block):
                upper = start + step
                for offset in range(step):
                    values[upper + offset] -= values[start + offset]
            step = block
    else:
        _normalize(values, mod)
        while step < size:
            block = step << 1
            for start in range(0, size, block):
                upper = start + step
                for offset in range(step):
                    index = upper + offset
                    values[index] = (
                        values[index] - values[start + offset]
                    ) % mod
            step = block
    return values


def superset_zeta_transform(values, mod=None):
    size = len(values)
    _check_size(size)
    step = 1
    if mod is None:
        while step < size:
            block = step << 1
            for start in range(0, size, block):
                upper = start + step
                for offset in range(step):
                    values[start + offset] += values[upper + offset]
            step = block
    else:
        _normalize(values, mod)
        while step < size:
            block = step << 1
            for start in range(0, size, block):
                upper = start + step
                for offset in range(step):
                    index = start + offset
                    values[index] = (
                        values[index] + values[upper + offset]
                    ) % mod
            step = block
    return values


def superset_mobius_transform(values, mod=None):
    size = len(values)
    _check_size(size)
    step = 1
    if mod is None:
        while step < size:
            block = step << 1
            for start in range(0, size, block):
                upper = start + step
                for offset in range(step):
                    values[start + offset] -= values[upper + offset]
            step = block
    else:
        _normalize(values, mod)
        while step < size:
            block = step << 1
            for start in range(0, size, block):
                upper = start + step
                for offset in range(step):
                    index = start + offset
                    values[index] = (
                        values[index] - values[upper + offset]
                    ) % mod
            step = block
    return values


def walsh_hadamard_transform(values, inverse=False, mod=None):
    size = len(values)
    _check_size(size)
    step = 1
    if mod is None:
        while step < size:
            block = step << 1
            for start in range(0, size, block):
                upper = start + step
                for offset in range(step):
                    left = values[start + offset]
                    right = values[upper + offset]
                    values[start + offset] = left + right
                    values[upper + offset] = left - right
            step = block
        if inverse:
            for index in range(size):
                values[index] //= size
    else:
        _normalize(values, mod)
        while step < size:
            block = step << 1
            for start in range(0, size, block):
                upper = start + step
                for offset in range(step):
                    left = values[start + offset]
                    right = values[upper + offset]
                    values[start + offset] = (left + right) % mod
                    values[upper + offset] = (left - right) % mod
            step = block
        if inverse:
            try:
                inverse_size = pow(size, -1, mod)
            except ValueError as error:
                raise ZeroDivisionError(
                    "transform length is not invertible modulo mod"
                ) from error
            for index in range(size):
                values[index] = values[index] * inverse_size % mod
    return values


def bitwise_or_convolution(first, second, mod=DEFAULT_MOD):
    _check_pair(first, second)
    left = [value % mod for value in first]
    right = [value % mod for value in second]
    subset_zeta_transform(left, mod)
    subset_zeta_transform(right, mod)
    for index in range(len(left)):
        left[index] = left[index] * right[index] % mod
    subset_mobius_transform(left, mod)
    return left


def bitwise_and_convolution(first, second, mod=DEFAULT_MOD):
    _check_pair(first, second)
    left = [value % mod for value in first]
    right = [value % mod for value in second]
    superset_zeta_transform(left, mod)
    superset_zeta_transform(right, mod)
    for index in range(len(left)):
        left[index] = left[index] * right[index] % mod
    superset_mobius_transform(left, mod)
    return left


def bitwise_xor_convolution(first, second, mod=DEFAULT_MOD):
    _check_pair(first, second)
    left = [value % mod for value in first]
    right = [value % mod for value in second]
    walsh_hadamard_transform(left, False, mod)
    walsh_hadamard_transform(right, False, mod)
    for index in range(len(left)):
        left[index] = left[index] * right[index] % mod
    walsh_hadamard_transform(left, True, mod)
    return left


class SubsetConvolution:
    __slots__ = ("mod",)

    def __init__(self, mod=DEFAULT_MOD):
        if mod <= 1:
            raise ValueError("mod must define a field")
        self.mod = mod

    def _lift_and_zeta(self, first, second):
        size = len(first)
        bits = (size - 1).bit_length()
        width = bits + 1
        popcount = _popcounts(size)
        total = size * width
        left = [0] * total
        right = [0] * total
        mod = self.mod
        for mask in range(size):
            position = mask * width + popcount[mask]
            left[position] = first[mask] % mod
            right[position] = second[mask] % mod
        step = 1
        while step < size:
            block = step << 1
            for start in range(0, size, block):
                for offset in range(step):
                    source = start + offset
                    target = source + step
                    source_position = source * width
                    target_position = target * width
                    limit = popcount[target]
                    for rank in range(limit):
                        left[target_position + rank] += left[
                            source_position + rank
                        ]
                        right[target_position + rank] += right[
                            source_position + rank
                        ]
            step = block
        return left, right, popcount, bits, width

    def _mobius_and_unlift(self, values, popcount, bits, width):
        size = len(popcount)
        step = size >> 1
        while step:
            block = step << 1
            for start in range(0, size, block):
                for offset in range(step):
                    source = start + offset
                    target = source + step
                    source_position = source * width
                    target_position = target * width
                    for rank in range(popcount[target], bits + 1):
                        values[target_position + rank] -= values[
                            source_position + rank
                        ]
            step >>= 1
        mod = self.mod
        return [
            values[mask * width + popcount[mask]] % mod
            for mask in range(size)
        ]

    def multiply(self, first, second):
        _check_pair(first, second)
        left, right, popcount, bits, width = self._lift_and_zeta(
            first, second
        )
        mod = self.mod
        scratch = [0] * width
        for mask, degree in enumerate(popcount):
            position = mask * width
            for total_degree in range(bits + 1):
                lower = max(0, total_degree - degree)
                upper = min(total_degree, degree)
                value = 0
                for rank in range(lower, upper + 1):
                    value += (
                        left[position + rank]
                        * right[position + total_degree - rank]
                    )
                scratch[total_degree] = value % mod
            for rank in range(width):
                left[position + rank] = scratch[rank]
        return self._mobius_and_unlift(
            left, popcount, bits, width
        )

    def divide(self, dividend, divisor):
        _check_pair(dividend, divisor)
        try:
            inverse_constant = pow(divisor[0] % self.mod, -1, self.mod)
        except ValueError as error:
            raise ZeroDivisionError(
                "divisor[0] must be invertible modulo mod"
            ) from error
        left, right, popcount, bits, width = self._lift_and_zeta(
            dividend, divisor
        )
        mod = self.mod
        scratch = [0] * width
        for mask in range(len(popcount)):
            position = mask * width
            for degree in range(bits + 1):
                value = left[position + degree]
                for rank in range(degree):
                    value -= scratch[rank] * right[
                        position + degree - rank
                    ]
                scratch[degree] = value * inverse_constant % mod
            for degree in range(width):
                left[position + degree] = scratch[degree]
        return self._mobius_and_unlift(
            left, popcount, bits, width
        )

    def transpose_multiply(self, first, second):
        result = self.multiply(list(reversed(first)), second)
        result.reverse()
        return result

    def exponential(self, series):
        _check_size(len(series))
        if series[0] % self.mod:
            raise ValueError("set-series exponential requires series[0] = 0")
        result = [0] * len(series)
        result[0] = 1
        bits = (len(series) - 1).bit_length()
        for bit in range(bits):
            half = 1 << bit
            upper = half << 1
            result[half:upper] = self.multiply(
                result[:half], series[half:upper]
            )
        return result

    def logarithm(self, series):
        _check_size(len(series))
        if series[0] % self.mod != 1:
            raise ValueError("set-series logarithm requires series[0] = 1")
        result = [0] * len(series)
        bits = (len(series) - 1).bit_length()
        for bit in range(bits - 1, -1, -1):
            half = 1 << bit
            upper = half << 1
            result[half:upper] = self.divide(
                series[half:upper], series[:half]
            )
        return result

    def compose_egf(self, series, derivatives):
        _check_size(len(series))
        if series[0] % self.mod:
            raise ValueError("EGF composition requires series[0] = 0")
        bits = (len(series) - 1).bit_length()
        coefficients = [value % self.mod for value in derivatives[:bits + 1]]
        coefficients.extend([0] * (bits + 1 - len(coefficients)))
        current = [coefficients[bits]]
        for degree in range(bits - 1, -1, -1):
            stages = bits - degree
            next_values = [0] * (1 << stages)
            next_values[0] = coefficients[degree]
            for stage in range(stages):
                half = 1 << stage
                next_values[half:half << 1] = self.multiply(
                    current[:half], series[half:half << 1]
                )
            current = next_values
        return current

    def compose(self, outer, series):
        _check_size(len(series))
        from library_codex.convolution.FormalPowerSeries import (
            fps_taylor_shift,
        )

        bits = (len(series) - 1).bit_length()
        shifted = fps_taylor_shift(outer, series[0], self.mod) if outer else []
        shifted.extend([0] * (bits + 1 - len(shifted)))
        factorial = 1
        derivatives = [0] * (bits + 1)
        for degree in range(bits + 1):
            if degree:
                factorial = factorial * degree % self.mod
            derivatives[degree] = shifted[degree] * factorial % self.mod
        zero_constant = [value % self.mod for value in series]
        zero_constant[0] = 0
        return self.compose_egf(zero_constant, derivatives)

    def transpose_compose_egf(self, series, weights):
        _check_pair(series, weights)
        if series[0] % self.mod:
            raise ValueError("transpose EGF composition requires series[0] = 0")
        bits = (len(series) - 1).bit_length()
        current = [value % self.mod for value in weights]
        result = [0] * (bits + 1)
        result[0] = current[0]
        for degree in range(bits):
            next_size = 1 << (bits - degree - 1)
            next_values = [0] * next_size
            for stage in range(bits - degree - 1, -1, -1):
                half = 1 << stage
                product = self.transpose_multiply(
                    current[half:half << 1],
                    series[half:half << 1],
                )
                for index, value in enumerate(product):
                    next_values[index] = (
                        next_values[index] + value
                    ) % self.mod
            current = next_values
            result[degree + 1] = current[0]
        return result

    def power_projection(self, series, weights, terms, exponential=False):
        _check_pair(series, weights)
        if terms < 0:
            raise ValueError("terms must be nonnegative")
        if terms == 0:
            return []
        mod = self.mod
        constant = series[0] % mod
        zero_constant = [value % mod for value in series]
        zero_constant[0] = 0
        derivatives = self.transpose_compose_egf(
            zero_constant, weights
        )
        bits = len(derivatives) - 1
        limit = max(bits, terms - 1)
        if limit >= mod:
            raise ValueError("factorials must be invertible modulo mod")
        factorial = [1] * (limit + 1)
        for index in range(1, limit + 1):
            factorial[index] = factorial[index - 1] * index % mod
        inverse_factorial = [1] * (limit + 1)
        inverse_factorial[-1] = pow(factorial[-1], -1, mod)
        for index in range(limit, 0, -1):
            inverse_factorial[index - 1] = (
                inverse_factorial[index] * index % mod
            )
        coefficients = [0] * terms
        power = 1
        for shift in range(terms):
            scale = power * inverse_factorial[shift] % mod
            upper = min(bits, terms - 1 - shift)
            for degree in range(upper + 1):
                coefficients[shift + degree] = (
                    coefficients[shift + degree]
                    + scale * derivatives[degree]
                ) % mod
            power = power * constant % mod
        for index in range(terms):
            coefficients[index] = coefficients[index] * factorial[index] % mod
            if exponential:
                coefficients[index] = (
                    coefficients[index] * inverse_factorial[index] % mod
                )
        return coefficients


def subset_convolution(first, second, mod=DEFAULT_MOD):
    return SubsetConvolution(mod).multiply(first, second)


def subset_convolution_divide(dividend, divisor, mod=DEFAULT_MOD):
    return SubsetConvolution(mod).divide(dividend, divisor)


def set_series_exponential(series, mod=DEFAULT_MOD):
    return SubsetConvolution(mod).exponential(series)


def set_series_logarithm(series, mod=DEFAULT_MOD):
    return SubsetConvolution(mod).logarithm(series)


def set_series_composition(outer, series, mod=DEFAULT_MOD):
    return SubsetConvolution(mod).compose(outer, series)


def set_series_power_projection(
    series, weights, terms, mod=DEFAULT_MOD, exponential=False
):
    return SubsetConvolution(mod).power_projection(
        series, weights, terms, exponential
    )


or_convolution = bitwise_or_convolution
and_convolution = bitwise_and_convolution
xor_convolution = bitwise_xor_convolution
walsh_hadamard_tranform = walsh_hadamard_transform
polynomial_composite_set_power_series = set_series_composition
power_projection_of_set_power_series = set_series_power_projection
