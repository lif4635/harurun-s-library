_NTT_CACHE = {}
_ARBITRARY_PRIMES = (469762049, 1811939329, 2013265921)
_ARBITRARY_PRODUCT = 469762049 * 1811939329 * 2013265921
_KNOWN_NTT_PRIMES = {
    998244353,
    924844033,
    1012924417,
    *_ARBITRARY_PRIMES,
}


def primitive_root(mod):
    if mod == 2:
        return 1
    value = mod - 1
    factors = []
    divisor = 2
    current = value
    while divisor * divisor <= current:
        if current % divisor == 0:
            factors.append(divisor)
            while current % divisor == 0:
                current //= divisor
        divisor += 1 if divisor == 2 else 2
    if current > 1:
        factors.append(current)
    candidate = 2
    while candidate < mod:
        for factor in factors:
            if pow(candidate, value // factor, mod) == 1:
                break
        else:
            return candidate
        candidate += 1
    raise ValueError("primitive root was not found")


class NumberTheoreticTransform:
    __slots__ = (
        "mod", "primitive_root", "rank2", "imag", "iimag",
        "rate2", "irate2", "rate3", "irate3",
    )

    def __init__(self, mod=998244353, root=None):
        if mod < 2:
            raise ValueError("mod must be at least 2")
        if root is None:
            root = primitive_root(mod)
        rank2 = ((mod - 1) & -(mod - 1)).bit_length() - 1
        self.mod = mod
        self.primitive_root = root
        self.rank2 = rank2
        roots = [0] * (rank2 + 1)
        inverse_roots = [0] * (rank2 + 1)
        roots[rank2] = pow(root, (mod - 1) >> rank2, mod)
        inverse_roots[rank2] = pow(roots[rank2], mod - 2, mod)
        for index in range(rank2 - 1, -1, -1):
            roots[index] = roots[index + 1] * roots[index + 1] % mod
            inverse_roots[index] = (
                inverse_roots[index + 1] * inverse_roots[index + 1] % mod
            )
        self.imag = roots[2] if rank2 >= 2 else 0
        self.iimag = inverse_roots[2] if rank2 >= 2 else 0

        rate2 = [0]
        irate2 = [0]
        product = 1
        inverse_product = 1
        for index in range(max(0, rank2 - 1)):
            rate2.append(roots[index + 2] * product % mod)
            irate2.append(
                inverse_roots[index + 2] * inverse_product % mod
            )
            product = product * inverse_roots[index + 2] % mod
            inverse_product = inverse_product * roots[index + 2] % mod
        rate2.append(0)
        irate2.append(0)
        self.rate2 = rate2
        self.irate2 = irate2

        rate3 = [0]
        irate3 = [0]
        product = 1
        inverse_product = 1
        for index in range(max(0, rank2 - 2)):
            rate3.append(roots[index + 3] * product % mod)
            irate3.append(
                inverse_roots[index + 3] * inverse_product % mod
            )
            product = product * inverse_roots[index + 3] % mod
            inverse_product = inverse_product * roots[index + 3] % mod
        rate3.append(0)
        irate3.append(0)
        self.rate3 = rate3
        self.irate3 = irate3

    def _check_length(self, size):
        if size < 1 or size & (size - 1):
            raise ValueError("NTT length must be a positive power of two")
        if size > 1 << self.rank2:
            raise ValueError("NTT length is unsupported by this modulus")

    def butterfly(self, values):
        size = len(values)
        self._check_length(size)
        if size == 1:
            values[0] %= self.mod
            return values
        mod = self.mod
        height = (size - 1).bit_length()
        level = 0
        imag = self.imag
        rate2 = self.rate2
        rate3 = self.rate3
        while level < height:
            if height - level == 1:
                width = 1 << (height - level - 1)
                rotation = 1
                for block in range(1 << level):
                    offset = block << (height - level)
                    for index in range(width):
                        left = values[offset + index]
                        right = values[offset + index + width] * rotation
                        values[offset + index] = (left + right) % mod
                        values[offset + index + width] = (left - right) % mod
                    rotation = (
                        rotation
                        * rate2[(~block & -~block).bit_length()]
                        % mod
                    )
                level += 1
            else:
                width = 1 << (height - level - 2)
                rotation = 1
                for block in range(1 << level):
                    rotation2 = rotation * rotation % mod
                    rotation3 = rotation2 * rotation % mod
                    offset = block << (height - level)
                    for index in range(width):
                        value0 = values[offset + index]
                        value1 = (
                            values[offset + index + width] * rotation
                        )
                        value2 = (
                            values[offset + index + 2 * width] * rotation2
                        )
                        value3 = (
                            values[offset + index + 3 * width] * rotation3
                        )
                        difference = (value1 - value3) % mod * imag
                        values[offset + index] = (
                            value0 + value2 + value1 + value3
                        ) % mod
                        values[offset + index + width] = (
                            value0 + value2 - value1 - value3
                        ) % mod
                        values[offset + index + 2 * width] = (
                            value0 - value2 + difference
                        ) % mod
                        values[offset + index + 3 * width] = (
                            value0 - value2 - difference
                        ) % mod
                    rotation = (
                        rotation
                        * rate3[(~block & -~block).bit_length()]
                        % mod
                    )
                level += 2
        return values

    def butterfly_inv(self, values, normalize=True):
        size = len(values)
        self._check_length(size)
        if size == 1:
            values[0] %= self.mod
            return values
        mod = self.mod
        height = (size - 1).bit_length()
        level = height
        inverse_imag = self.iimag
        irate2 = self.irate2
        irate3 = self.irate3
        while level:
            if level == 1:
                width = 1 << (height - level)
                rotation = 1
                for block in range(1 << (level - 1)):
                    offset = block << (height - level + 1)
                    for index in range(width):
                        left = values[offset + index]
                        right = values[offset + index + width]
                        values[offset + index] = (left + right) % mod
                        values[offset + index + width] = (
                            (left - right) * rotation % mod
                        )
                    rotation = (
                        rotation
                        * irate2[(~block & -~block).bit_length()]
                        % mod
                    )
                level -= 1
            else:
                width = 1 << (height - level)
                rotation = 1
                for block in range(1 << (level - 2)):
                    rotation2 = rotation * rotation % mod
                    rotation3 = rotation2 * rotation % mod
                    offset = block << (height - level + 2)
                    for index in range(width):
                        value0 = values[offset + index]
                        value1 = values[offset + index + width]
                        value2 = values[offset + index + 2 * width]
                        value3 = values[offset + index + 3 * width]
                        difference = (
                            (value2 - value3) * inverse_imag % mod
                        )
                        values[offset + index] = (
                            value0 + value1 + value2 + value3
                        ) % mod
                        values[offset + index + width] = (
                            (value0 - value1 + difference) * rotation % mod
                        )
                        values[offset + index + 2 * width] = (
                            (value0 + value1 - value2 - value3)
                            * rotation2
                            % mod
                        )
                        values[offset + index + 3 * width] = (
                            (value0 - value1 - difference) * rotation3 % mod
                        )
                    rotation = (
                        rotation
                        * irate3[(~block & -~block).bit_length()]
                        % mod
                    )
                level -= 2
        if normalize:
            inverse_size = pow(size, mod - 2, mod)
            for index in range(size):
                values[index] = values[index] * inverse_size % mod
        return values

    def transform(self, values, inverse=False):
        if inverse:
            return self.butterfly_inv(values)
        return self.butterfly(values)

    def convolution(self, first, second, naive_threshold=60):
        first_size = len(first)
        second_size = len(second)
        if first_size == 0 or second_size == 0:
            return []
        mod = self.mod
        output_size = first_size + second_size - 1
        if min(first_size, second_size) <= naive_threshold:
            return convolution_naive(first, second, mod)
        size = 1 << (output_size - 1).bit_length()
        self._check_length(size)
        left = [value % mod for value in first]
        left.extend([0] * (size - first_size))
        self.butterfly(left)
        if first is second:
            for index in range(size):
                left[index] = left[index] * left[index] % mod
        else:
            right = [value % mod for value in second]
            right.extend([0] * (size - second_size))
            self.butterfly(right)
            for index in range(size):
                left[index] = left[index] * right[index] % mod
        self.butterfly_inv(left)
        del left[output_size:]
        return left


NumberTheroemTransform = NumberTheoreticTransform


def get_ntt(mod=998244353, root=None):
    key = mod, root
    transform = _NTT_CACHE.get(key)
    if transform is None:
        transform = NumberTheoreticTransform(mod, root)
        _NTT_CACHE[key] = transform
    return transform


def convolution_naive(first, second, mod=None):
    if not first or not second:
        return []
    result = [0] * (len(first) + len(second) - 1)
    if len(first) > len(second):
        first, second = second, first
    if mod is None:
        for left_index, left in enumerate(first):
            for right_index, right in enumerate(second):
                result[left_index + right_index] += left * right
    else:
        for left_index, left in enumerate(first):
            left %= mod
            for right_index, right in enumerate(second):
                position = left_index + right_index
                result[position] += left * (right % mod)
            if left_index & 7 == 7:
                for index in range(left_index, left_index + len(second)):
                    result[index] %= mod
        for index in range(len(result)):
            result[index] %= mod
    return result


def convolution_ntt(first, second, mod=998244353, root=None):
    return get_ntt(mod, root).convolution(first, second)


def _crt_convolutions(first, second):
    return [
        convolution_ntt(first, second, mod) for mod in _ARBITRARY_PRIMES
    ]


def convolution_any_mod(first, second, mod):
    if mod <= 0:
        raise ValueError("mod must be positive")
    if not first or not second:
        return []
    if mod == 1:
        return [0] * (len(first) + len(second) - 1)
    if min(len(first), len(second)) <= 60:
        return convolution_naive(first, second, mod)
    normalized_first = [value % mod for value in first]
    normalized_second = [value % mod for value in second]
    bound = (
        min(len(first), len(second))
        * max(normalized_first, default=0)
        * max(normalized_second, default=0)
    )
    if bound >= _ARBITRARY_PRODUCT:
        raise OverflowError("modular convolution exceeds the CRT range")
    residues = _crt_convolutions(normalized_first, normalized_second)
    mod1, mod2, mod3 = _ARBITRARY_PRIMES
    inverse1 = pow(mod1, -1, mod2)
    mod12 = mod1 * mod2
    inverse12 = pow(mod12 % mod3, -1, mod3)
    result = [0] * len(residues[0])
    first_residue, second_residue, third_residue = residues
    for index in range(len(result)):
        value1 = first_residue[index]
        coefficient2 = (
            (second_residue[index] - value1) * inverse1 % mod2
        )
        value12 = value1 + mod1 * coefficient2
        coefficient3 = (
            (third_residue[index] - value12) * inverse12 % mod3
        )
        result[index] = (value12 + mod12 * coefficient3) % mod
    return result


def convolution_int(first, second):
    if not first or not second:
        return []
    if min(len(first), len(second)) <= 60:
        return convolution_naive(first, second)
    product = _ARBITRARY_PRODUCT
    bound = (
        min(len(first), len(second))
        * max(map(abs, first), default=0)
        * max(map(abs, second), default=0)
    )
    if bound >= product // 2:
        raise OverflowError("integer convolution exceeds the CRT range")
    residues = _crt_convolutions(first, second)
    mod1, mod2, mod3 = _ARBITRARY_PRIMES
    inverse1 = pow(mod1, -1, mod2)
    mod12 = mod1 * mod2
    inverse12 = pow(mod12 % mod3, -1, mod3)
    result = [0] * len(residues[0])
    first_residue, second_residue, third_residue = residues
    half = product // 2
    for index in range(len(result)):
        value1 = first_residue[index]
        coefficient2 = (
            (second_residue[index] - value1) * inverse1 % mod2
        )
        value12 = value1 + mod1 * coefficient2
        coefficient3 = (
            (third_residue[index] - value12) * inverse12 % mod3
        )
        value = value12 + mod12 * coefficient3
        result[index] = value - product if value > half else value
    return result


def convolution(first, second, mod=998244353):
    if not first or not second:
        return []
    output_size = len(first) + len(second) - 1
    size = 1 << (output_size - 1).bit_length()
    if mod in _KNOWN_NTT_PRIMES and (mod - 1) % size == 0:
        return convolution_ntt(first, second, mod)
    return convolution_any_mod(first, second, mod)
