_convolution_ntt_NTT_CACHE = {}
_convolution_ntt_DEFAULT_MOD = 998244353
_convolution_ntt_DEFAULT_ROOT = 3
_convolution_ntt_ARBITRARY_PRIMES = (469762049, 1811939329, 2013265921)
_convolution_ntt_ARBITRARY_PRODUCT = 469762049 * 1811939329 * 2013265921
_convolution_ntt_KNOWN_NTT_PRIMES = {998244353, 924844033, 1012924417, *_convolution_ntt_ARBITRARY_PRIMES}

def primitive_root(mod):
    """Return a primitive root modulo ``mod``. O(sqrt(mod)) worst case."""
    if mod == 2:
        return 1
    if mod == _convolution_ntt_DEFAULT_MOD:
        return _convolution_ntt_DEFAULT_ROOT
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
    raise ValueError('primitive root was not found')

class NumberTheoreticTransform:
    """Reusable radix-4 NTT tables for one prime modulus."""
    __slots__ = ('mod', 'primitive_root', 'rank2', 'imag', 'iimag', 'rate2', 'irate2', 'rate3', 'irate3', '_inverse_sizes')

    def __init__(self, mod=998244353, root=None):
        if mod < 2:
            raise ValueError('mod must be at least 2')
        if root is None:
            root = primitive_root(mod)
        rank2 = (mod - 1 & -(mod - 1)).bit_length() - 1
        self.mod = mod
        self.primitive_root = root
        self.rank2 = rank2
        roots = [0] * (rank2 + 1)
        inverse_roots = [0] * (rank2 + 1)
        roots[rank2] = pow(root, mod - 1 >> rank2, mod)
        inverse_roots[rank2] = pow(roots[rank2], mod - 2, mod)
        for index in range(rank2 - 1, -1, -1):
            roots[index] = roots[index + 1] * roots[index + 1] % mod
            inverse_roots[index] = inverse_roots[index + 1] * inverse_roots[index + 1] % mod
        self.imag = roots[2] if rank2 >= 2 else 0
        self.iimag = inverse_roots[2] if rank2 >= 2 else 0
        rate2 = [0]
        irate2 = [0]
        product = 1
        inverse_product = 1
        for index in range(max(0, rank2 - 1)):
            rate2.append(roots[index + 2] * product % mod)
            irate2.append(inverse_roots[index + 2] * inverse_product % mod)
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
            irate3.append(inverse_roots[index + 3] * inverse_product % mod)
            product = product * inverse_roots[index + 3] % mod
            inverse_product = inverse_product * roots[index + 3] % mod
        rate3.append(0)
        irate3.append(0)
        self.rate3 = rate3
        self.irate3 = irate3
        self._inverse_sizes = {1: 1}

    def _check_length(self, size):
        if size < 1 or size & size - 1:
            raise ValueError('NTT length must be a positive power of two')
        if size > 1 << self.rank2:
            raise ValueError('NTT length is unsupported by this modulus')

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
                width = 1 << height - level - 1
                rotation = 1
                for block in range(1 << level):
                    offset = block << height - level
                    for index in range(width):
                        left = values[offset + index]
                        right = values[offset + index + width] * rotation
                        values[offset + index] = (left + right) % mod
                        values[offset + index + width] = (left - right) % mod
                    rotation = rotation * rate2[(~block & -~block).bit_length()] % mod
                level += 1
            else:
                width = 1 << height - level - 2
                rotation = 1
                for block in range(1 << level):
                    rotation2 = rotation * rotation % mod
                    rotation3 = rotation2 * rotation % mod
                    offset = block << height - level
                    for index in range(width):
                        value0 = values[offset + index]
                        value1 = values[offset + index + width] * rotation
                        value2 = values[offset + index + 2 * width] * rotation2
                        value3 = values[offset + index + 3 * width] * rotation3
                        difference = (value1 - value3) % mod * imag
                        values[offset + index] = (value0 + value2 + value1 + value3) % mod
                        values[offset + index + width] = (value0 + value2 - value1 - value3) % mod
                        values[offset + index + 2 * width] = (value0 - value2 + difference) % mod
                        values[offset + index + 3 * width] = (value0 - value2 - difference) % mod
                    rotation = rotation * rate3[(~block & -~block).bit_length()] % mod
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
                width = 1 << height - level
                rotation = 1
                for block in range(1 << level - 1):
                    offset = block << height - level + 1
                    for index in range(width):
                        left = values[offset + index]
                        right = values[offset + index + width]
                        values[offset + index] = (left + right) % mod
                        values[offset + index + width] = (left - right) * rotation % mod
                    rotation = rotation * irate2[(~block & -~block).bit_length()] % mod
                level -= 1
            else:
                width = 1 << height - level
                rotation = 1
                for block in range(1 << level - 2):
                    rotation2 = rotation * rotation % mod
                    rotation3 = rotation2 * rotation % mod
                    offset = block << height - level + 2
                    for index in range(width):
                        value0 = values[offset + index]
                        value1 = values[offset + index + width]
                        value2 = values[offset + index + 2 * width]
                        value3 = values[offset + index + 3 * width]
                        difference = (value2 - value3) * inverse_imag % mod
                        values[offset + index] = (value0 + value1 + value2 + value3) % mod
                        values[offset + index + width] = (value0 - value1 + difference) * rotation % mod
                        values[offset + index + 2 * width] = (value0 + value1 - value2 - value3) * rotation2 % mod
                        values[offset + index + 3 * width] = (value0 - value1 - difference) * rotation3 % mod
                    rotation = rotation * irate3[(~block & -~block).bit_length()] % mod
                level -= 2
        if normalize:
            inverse_size = self._inverse_sizes.get(size)
            if inverse_size is None:
                inverse_size = pow(size, mod - 2, mod)
                self._inverse_sizes[size] = inverse_size
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
_convolution_ntt_DEFAULT_NTT = NumberTheoreticTransform(_convolution_ntt_DEFAULT_MOD, _convolution_ntt_DEFAULT_ROOT)
_convolution_ntt_NTT_CACHE[_convolution_ntt_DEFAULT_MOD, None] = _convolution_ntt_DEFAULT_NTT

def get_ntt(mod=998244353, root=None):
    """Return the cached transform for ``mod`` and ``root``. O(1) after setup."""
    key = (mod, root)
    transform = _convolution_ntt_NTT_CACHE.get(key)
    if transform is None:
        transform = NumberTheoreticTransform(mod, root)
        _convolution_ntt_NTT_CACHE[key] = transform
    return transform

def convolution_naive(first, second, mod=None):
    """Multiply coefficient lists directly. O(len(first) * len(second))."""
    if not first or not second:
        return []
    result = [0] * (len(first) + len(second) - 1)
    if len(first) > len(second):
        (first, second) = (second, first)
    if mod is None:
        for (left_index, left) in enumerate(first):
            for (right_index, right) in enumerate(second):
                result[left_index + right_index] += left * right
    else:
        for (left_index, left) in enumerate(first):
            left %= mod
            for (right_index, right) in enumerate(second):
                position = left_index + right_index
                result[position] += left * (right % mod)
            if left_index & 7 == 7:
                for index in range(left_index, left_index + len(second)):
                    result[index] %= mod
        for index in range(len(result)):
            result[index] %= mod
    return result

def convolution_ntt(first, second, mod=998244353, root=None):
    """Multiply with a cached NTT for a friendly prime. O(N log N)."""
    return get_ntt(mod, root).convolution(first, second)

def _convolution_ntt_crt_convolutions(first, second):
    return [convolution_ntt(first, second, mod) for mod in _convolution_ntt_ARBITRARY_PRIMES]

def convolution_any_mod(first, second, mod):
    """Multiply modulo an arbitrary positive integer using three NTTs. O(N log N)."""
    if mod <= 0:
        raise ValueError('mod must be positive')
    if not first or not second:
        return []
    if mod == 1:
        return [0] * (len(first) + len(second) - 1)
    if min(len(first), len(second)) <= 60:
        return convolution_naive(first, second, mod)
    normalized_first = [value % mod for value in first]
    normalized_second = [value % mod for value in second]
    bound = min(len(first), len(second)) * max(normalized_first, default=0) * max(normalized_second, default=0)
    if bound >= _convolution_ntt_ARBITRARY_PRODUCT:
        raise OverflowError('modular convolution exceeds the CRT range')
    residues = _convolution_ntt_crt_convolutions(normalized_first, normalized_second)
    (mod1, mod2, mod3) = _convolution_ntt_ARBITRARY_PRIMES
    inverse1 = pow(mod1, -1, mod2)
    mod12 = mod1 * mod2
    inverse12 = pow(mod12 % mod3, -1, mod3)
    result = [0] * len(residues[0])
    (first_residue, second_residue, third_residue) = residues
    for index in range(len(result)):
        value1 = first_residue[index]
        coefficient2 = (second_residue[index] - value1) * inverse1 % mod2
        value12 = value1 + mod1 * coefficient2
        coefficient3 = (third_residue[index] - value12) * inverse12 % mod3
        result[index] = (value12 + mod12 * coefficient3) % mod
    return result

def convolution_int(first, second):
    """Multiply integer coefficient lists exactly within the CRT bound. O(N log N)."""
    if not first or not second:
        return []
    if min(len(first), len(second)) <= 60:
        return convolution_naive(first, second)
    product = _convolution_ntt_ARBITRARY_PRODUCT
    bound = min(len(first), len(second)) * max(map(abs, first), default=0) * max(map(abs, second), default=0)
    if bound >= product // 2:
        raise OverflowError('integer convolution exceeds the CRT range')
    residues = _convolution_ntt_crt_convolutions(first, second)
    (mod1, mod2, mod3) = _convolution_ntt_ARBITRARY_PRIMES
    inverse1 = pow(mod1, -1, mod2)
    mod12 = mod1 * mod2
    inverse12 = pow(mod12 % mod3, -1, mod3)
    result = [0] * len(residues[0])
    (first_residue, second_residue, third_residue) = residues
    half = product // 2
    for index in range(len(result)):
        value1 = first_residue[index]
        coefficient2 = (second_residue[index] - value1) * inverse1 % mod2
        value12 = value1 + mod1 * coefficient2
        coefficient3 = (third_residue[index] - value12) * inverse12 % mod3
        value = value12 + mod12 * coefficient3
        result[index] = value - product if value > half else value
    return result

def convolution(first, second, mod=998244353):
    """Multiply coefficient lists; 998244353 uses the cached direct NTT. O(N log N)."""
    if not first or not second:
        return []
    output_size = len(first) + len(second) - 1
    size = 1 << (output_size - 1).bit_length()
    if mod in _convolution_ntt_KNOWN_NTT_PRIMES and (mod - 1) % size == 0:
        return convolution_ntt(first, second, mod)
    return convolution_any_mod(first, second, mod)
from math import gcd, isqrt

def modular_square_root(value, prime):
    if prime < 2:
        raise ValueError('prime must be at least 2')
    value %= prime
    if value < 2 or prime == 2:
        return value
    if pow(value, prime - 1 >> 1, prime) != 1:
        return -1
    if prime & 3 == 3:
        root = pow(value, prime + 1 >> 2, prime)
        return min(root, prime - root)
    odd = prime - 1
    exponent = 0
    while odd & 1 == 0:
        odd >>= 1
        exponent += 1
    nonresidue = 2
    while pow(nonresidue, prime - 1 >> 1, prime) != prime - 1:
        nonresidue += 1
    root = pow(value, odd + 1 >> 1, prime)
    remainder = pow(value, odd, prime)
    generator = pow(nonresidue, odd, prime)
    level = exponent
    while remainder != 1:
        position = 1
        squared = remainder * remainder % prime
        while position < level and squared != 1:
            squared = squared * squared % prime
            position += 1
        if position == level:
            return -1
        adjustment = pow(generator, 1 << level - position - 1, prime)
        root = root * adjustment % prime
        adjustment = adjustment * adjustment % prime
        remainder = remainder * adjustment % prime
        generator = adjustment
        level = position
    return min(root, prime - root)

def discrete_logarithm(base, target, modulus):
    if modulus <= 0:
        raise ValueError('modulus must be positive')
    base %= modulus
    target %= modulus
    identity = 1 % modulus
    if target == identity:
        return 0
    offset = 0
    accumulated = identity
    while True:
        common = gcd(base, modulus)
        if common == 1:
            break
        if target == accumulated:
            return offset
        if target % common:
            return -1
        target //= common
        modulus //= common
        offset += 1
        if modulus == 1:
            return offset
        accumulated = accumulated * (base // common) % modulus
    target = target * pow(accumulated, -1, modulus) % modulus
    width = isqrt(modulus) + 1
    baby = {}
    value = 1
    for exponent in range(width):
        if value not in baby:
            baby[value] = exponent
        value = value * base % modulus
    inverse_step = pow(value, -1, modulus)
    giant = target
    for block in range(width + 1):
        exponent = baby.get(giant)
        if exponent is not None:
            return offset + block * width + exponent
        giant = giant * inverse_step % modulus
    return -1
mod_sqrt = modular_square_root
tonelli_shanks = modular_square_root
mod_log = discrete_logarithm
ModLog = discrete_logarithm
'Formal power series represented by ascending coefficient lists.\n\nThe default modulus is 998244353.  That path reuses one radix-4 NTT instance,\nits root tables, and inverse transform factors across all FPS operations.\nOther moduli keep the general NTT or CRT fallback.\n'
from heapq import heapify, heappop, heappush
DEFAULT_MOD = 998244353
_fps_formal_power_series_INVERSE_CACHE = {}
_fps_formal_power_series_DEFAULT_TRANSFORM = get_ntt(DEFAULT_MOD)
_fps_formal_power_series_SPARSE_INV_THRESHOLD = 160
_fps_formal_power_series_SPARSE_DIV_THRESHOLD = 200
_fps_formal_power_series_SPARSE_LOG_THRESHOLD = 200
_fps_formal_power_series_SPARSE_EXP_THRESHOLD = 320
_fps_formal_power_series_SPARSE_POWER_THRESHOLD = 32

def _fps_formal_power_series_degree(degree, default):
    if degree is None:
        return default
    if degree < 0:
        raise ValueError('degree must be nonnegative')
    return degree

def _fps_formal_power_series_inverses(size, mod):
    if size >= mod:
        raise ValueError('formal integration requires degree < mod')
    values = _fps_formal_power_series_INVERSE_CACHE.get(mod)
    if values is None:
        values = [0, 1]
        _fps_formal_power_series_INVERSE_CACHE[mod] = values
    for index in range(len(values), size + 1):
        values.append(-values[mod % index] * (mod // index) % mod)
    return values

def _fps_formal_power_series_sparse_terms(series, degree, mod, threshold):
    terms = []
    for index in range(1, min(len(series), degree)):
        value = series[index] % mod
        if value:
            terms.append((index, value))
            if len(terms) > threshold:
                return None
    return terms

def _fps_formal_power_series_fps_inverse_sparse(degree, first_inverse, terms, mod):
    result = [0] * degree
    result[0] = first_inverse
    for index in range(1, degree):
        total = 0
        for (offset, coefficient) in terms:
            if offset > index:
                break
            total += coefficient * result[index - offset]
        result[index] = -total * first_inverse % mod
    return result

def _fps_formal_power_series_fps_div_sparse(numerator, degree, first_inverse, terms, mod):
    result = [0] * degree
    for index in range(degree):
        total = numerator[index] % mod if index < len(numerator) else 0
        for (offset, coefficient) in terms:
            if offset > index:
                break
            total -= coefficient * result[index - offset]
        result[index] = total * first_inverse % mod
    return result

def _fps_formal_power_series_fps_logarithm_sparse(series, degree, terms, mod):
    inverse = _fps_formal_power_series_inverses(degree, mod)
    result = [0] * degree
    for index in range(1, degree):
        total = index * (series[index] % mod) if index < len(series) else 0
        for (offset, coefficient) in terms:
            if offset >= index:
                break
            total -= (index - offset) * coefficient * result[index - offset]
        result[index] = total * inverse[index] % mod
    return result

def _fps_formal_power_series_fps_exponential_sparse(degree, terms, mod):
    inverse = _fps_formal_power_series_inverses(degree, mod)
    result = [0] * degree
    result[0] = 1
    for index in range(1, degree):
        total = 0
        for (offset, coefficient) in terms:
            if offset > index:
                break
            total += offset * coefficient * result[index - offset]
        result[index] = total * inverse[index] % mod
    return result

def _fps_formal_power_series_fps_power_unit_sparse(degree, exponent, terms, mod):
    inverse = _fps_formal_power_series_inverses(degree, mod)
    result = [0] * degree
    result[0] = 1
    exponent %= mod
    for index in range(1, degree):
        total = 0
        for (offset, coefficient) in terms:
            if offset > index:
                break
            factor = (exponent * offset - index + offset) % mod
            total += factor * coefficient * result[index - offset]
        result[index] = total * inverse[index] % mod
    return result

def fps_shrink(series, mod=DEFAULT_MOD):
    """Return normalized coefficients without trailing zeroes. O(N)."""
    result = [value % mod for value in series]
    while result and result[-1] == 0:
        result.pop()
    return result

def shrink(series, mod=DEFAULT_MOD):
    """Normalize ``series`` in place and remove trailing zeroes. O(N)."""
    for index in range(len(series)):
        series[index] %= mod
    while series and series[-1] == 0:
        series.pop()
    return series

def fps_add(first, second, mod=DEFAULT_MOD):
    """Add two ascending coefficient lists modulo ``mod``. O(N)."""
    size = max(len(first), len(second))
    result = [0] * size
    common = min(len(first), len(second))
    for index in range(common):
        result[index] = (first[index] + second[index]) % mod
    for index in range(common, len(first)):
        result[index] = first[index] % mod
    for index in range(common, len(second)):
        result[index] = second[index] % mod
    return result

def fps_subtract(first, second, mod=DEFAULT_MOD):
    """Subtract the second coefficient list from the first. O(N)."""
    size = max(len(first), len(second))
    result = [0] * size
    common = min(len(first), len(second))
    for index in range(common):
        result[index] = (first[index] - second[index]) % mod
    for index in range(common, len(first)):
        result[index] = first[index] % mod
    for index in range(common, len(second)):
        result[index] = -second[index] % mod
    return result

def fps_negate(series, mod=DEFAULT_MOD):
    """Negate every coefficient modulo ``mod``. O(N)."""
    return [-value % mod for value in series]

def fps_multiply(first, second, mod=DEFAULT_MOD):
    """Multiply two series. The default modulus takes the direct cached NTT path. O(N log N)."""
    if mod == DEFAULT_MOD:
        return _fps_formal_power_series_DEFAULT_TRANSFORM.convolution(first, second)
    return convolution(first, second, mod)

def fps_derivative(series, mod=DEFAULT_MOD):
    """Return the formal derivative in ascending coefficient order. O(N)."""
    return [index * series[index] % mod for index in range(1, len(series))]

def fps_integral(series, mod=DEFAULT_MOD):
    """Return the formal integral with constant coefficient zero. O(N)."""
    inverse = _fps_formal_power_series_inverses(len(series), mod)
    result = [0] * (len(series) + 1)
    for (index, value) in enumerate(series, 1):
        result[index] = value * inverse[index] % mod
    return result

def fps_evaluate(series, value, mod=DEFAULT_MOD):
    """Evaluate the represented polynomial at ``value`` with Horner's rule. O(N)."""
    result = 0
    value %= mod
    for coefficient in reversed(series):
        result = (result * value + coefficient) % mod
    return result

def _fps_formal_power_series_inverse_ntt_step(series, result, current, target, transform):
    size = current << 1
    mod = transform.mod
    left = [value % mod for value in series[:target]]
    left.extend([0] * (size - len(left)))
    right = result + [0] * (size - current)
    transform.butterfly(left)
    transform.butterfly(right)
    for index in range(size):
        left[index] = left[index] * right[index] % mod
    transform.butterfly_inv(left)
    for index in range(current):
        left[index] = 0
    for index in range(current, target):
        left[index] = -left[index] % mod
    for index in range(target, size):
        left[index] = 0
    transform.butterfly(left)
    for index in range(size):
        left[index] = left[index] * right[index] % mod
    transform.butterfly_inv(left)
    result.extend(left[current:target])

def fps_inverse(series, degree=None, mod=DEFAULT_MOD):
    """Return coefficients of ``1 / series`` through ``degree``. O(N log N)."""
    degree = _fps_formal_power_series_degree(degree, len(series))
    if degree == 0:
        return []
    if not series:
        raise ZeroDivisionError('the zero series is not invertible')
    try:
        first_inverse = pow(series[0] % mod, -1, mod)
    except ValueError as error:
        raise ZeroDivisionError('the constant coefficient is not invertible') from error
    terms = _fps_formal_power_series_sparse_terms(series, degree, mod, _fps_formal_power_series_SPARSE_INV_THRESHOLD)
    if terms is not None:
        return _fps_formal_power_series_fps_inverse_sparse(degree, first_inverse, terms, mod)
    result = [first_inverse]
    current = 1
    transform = _fps_formal_power_series_DEFAULT_TRANSFORM if mod == DEFAULT_MOD else None
    if transform is None:
        try:
            transform = get_ntt(mod)
        except ValueError:
            pass
    while current < degree:
        target = min(current << 1, degree)
        direct = transform is not None
        if direct:
            try:
                transform._check_length(current << 1)
            except ValueError:
                direct = False
        if direct:
            _fps_formal_power_series_inverse_ntt_step(series, result, current, target, transform)
        else:
            product = fps_multiply(series[:target], result, mod)[:target]
            correction = [0] * target
            correction[0] = (2 - product[0]) % mod
            for index in range(1, len(product)):
                correction[index] = -product[index] % mod
            result = fps_multiply(result, correction, mod)[:target]
        current = target
    return result

def fps_div(numerator, denominator, degree=None, mod=DEFAULT_MOD):
    """Return ``numerator / denominator mod x^degree``. O(N log N)."""
    degree = _fps_formal_power_series_degree(degree, len(numerator))
    if degree == 0:
        return []
    if not denominator:
        raise ZeroDivisionError('fps division requires a denominator')
    try:
        first_inverse = pow(denominator[0] % mod, -1, mod)
    except ValueError as error:
        raise ZeroDivisionError('denominator constant coefficient must be invertible') from error
    terms = _fps_formal_power_series_sparse_terms(denominator, degree, mod, _fps_formal_power_series_SPARSE_DIV_THRESHOLD)
    if terms is not None:
        return _fps_formal_power_series_fps_div_sparse(numerator, degree, first_inverse, terms, mod)
    inverse = fps_inverse(denominator, degree, mod)
    result = fps_multiply(numerator[:degree], inverse, mod)[:degree]
    result.extend([0] * (degree - len(result)))
    return result

def fps_logarithm(series, degree=None, mod=DEFAULT_MOD):
    """Return the formal logarithm through ``degree``; series[0] must be 1. O(N log N)."""
    degree = _fps_formal_power_series_degree(degree, len(series))
    if degree == 0:
        return []
    if not series or series[0] % mod != 1:
        raise ValueError('fps logarithm requires constant coefficient 1')
    terms = _fps_formal_power_series_sparse_terms(series, degree, mod, _fps_formal_power_series_SPARSE_LOG_THRESHOLD)
    if terms is not None:
        return _fps_formal_power_series_fps_logarithm_sparse(series, degree, terms, mod)
    product = fps_multiply(fps_derivative(series, mod), fps_inverse(series, degree, mod), mod)
    result = fps_integral(product[:degree - 1], mod)
    result.extend([0] * (degree - len(result)))
    return result

def _fps_formal_power_series_fps_exponential_ntt(series, degree, transform):
    mod = transform.mod
    b = [1, series[1] % mod if len(series) > 1 else 0]
    c = [1]
    z2 = [1, 1]
    inverse = [0, 1]
    size = 2
    while size < degree:
        doubled = size << 1
        y = b + [0] * size
        transform.butterfly(y)
        z1 = z2
        z = [y[index] * z1[index] % mod for index in range(size)]
        transform.butterfly_inv(z)
        for index in range(size >> 1):
            z[index] = 0
        transform.butterfly(z)
        for index in range(size):
            z[index] = -z[index] * z1[index] % mod
        transform.butterfly_inv(z)
        c.extend(z[size >> 1:])
        z2 = c + [0] * size
        transform.butterfly(z2)
        source_size = min(len(series), size)
        x = [series[index] % mod for index in range(source_size)]
        x.extend([0] * (size - source_size))
        x = fps_derivative(x, mod)
        x.append(0)
        transform.butterfly(x)
        for index in range(size):
            x[index] = x[index] * y[index] % mod
        transform.butterfly_inv(x)
        for index in range(1, len(b)):
            x[index - 1] = (x[index - 1] - index * b[index]) % mod
        x.extend([0] * size)
        for index in range(size - 1):
            (x[size + index], x[index]) = (x[index], 0)
        transform.butterfly(x)
        for index in range(doubled):
            x[index] = x[index] * z2[index] % mod
        transform.butterfly_inv(x)
        x.pop()
        for index in range(len(inverse), len(x) + 1):
            inverse.append(-inverse[mod % index] * (mod // index) % mod)
        x = [0] + [value * inverse[index + 1] % mod for (index, value) in enumerate(x)]
        for index in range(size):
            x[index] = 0
        for index in range(size, min(len(series), doubled)):
            x[index] = (x[index] + series[index]) % mod
        transform.butterfly(x)
        for index in range(doubled):
            x[index] = x[index] * y[index] % mod
        transform.butterfly_inv(x)
        b.extend(x[size:])
        size = doubled
    return b[:degree]

def _fps_formal_power_series_fps_exponential_newton(series, degree, mod):
    result = [1]
    while len(result) < degree:
        target = min(len(result) << 1, degree)
        logarithm = fps_logarithm(result, target, mod)
        correction = [0] * target
        for index in range(target):
            value = series[index] if index < len(series) else 0
            correction[index] = (value - logarithm[index]) % mod
        correction[0] = (correction[0] + 1) % mod
        result = fps_multiply(result, correction, mod)[:target]
    return result

def fps_exponential(series, degree=None, mod=DEFAULT_MOD):
    """Return the formal exponential through ``degree``; series[0] must be 0. O(N log N)."""
    degree = _fps_formal_power_series_degree(degree, len(series))
    if degree == 0:
        return []
    if series and series[0] % mod:
        raise ValueError('fps exponential requires constant coefficient 0')
    terms = _fps_formal_power_series_sparse_terms(series, degree, mod, _fps_formal_power_series_SPARSE_EXP_THRESHOLD)
    if terms is not None:
        return _fps_formal_power_series_fps_exponential_sparse(degree, terms, mod)
    transform = _fps_formal_power_series_DEFAULT_TRANSFORM if mod == DEFAULT_MOD else None
    try:
        if transform is None:
            transform = get_ntt(mod)
        transform._check_length(1 << (degree - 1).bit_length())
    except ValueError:
        transform = None
    if transform is not None:
        return _fps_formal_power_series_fps_exponential_ntt(series, degree, transform)
    return _fps_formal_power_series_fps_exponential_newton(series, degree, mod)

def fps_power(series, exponent, degree=None, mod=DEFAULT_MOD):
    """Raise a series to an integer power through ``degree``. O(N log N)."""
    degree = _fps_formal_power_series_degree(degree, len(series))
    if degree == 0:
        return []
    if exponent == 0:
        return [1] + [0] * (degree - 1)
    leading = 0
    while leading < len(series) and series[leading] % mod == 0:
        leading += 1
    if leading == len(series):
        if exponent < 0:
            raise ZeroDivisionError('a zero series cannot have negative exponent')
        return [0] * degree
    if exponent < 0 and leading:
        raise ValueError('negative power requires an invertible series')
    shift = leading * exponent
    if shift >= degree:
        return [0] * degree
    coefficient = series[leading] % mod
    try:
        inverse_coefficient = pow(coefficient, -1, mod)
    except ValueError as error:
        raise ZeroDivisionError('the leading coefficient is not invertible') from error
    needed = degree - shift
    normalized = [value * inverse_coefficient % mod for value in series[leading:]]
    terms = _fps_formal_power_series_sparse_terms(normalized, needed, mod, _fps_formal_power_series_SPARSE_POWER_THRESHOLD)
    if terms is not None:
        result = _fps_formal_power_series_fps_power_unit_sparse(needed, exponent, terms, mod)
    else:
        logarithm = fps_logarithm(normalized, needed, mod)
        for index in range(needed):
            logarithm[index] = logarithm[index] * exponent % mod
        result = fps_exponential(logarithm, needed, mod)
    scale = pow(coefficient, exponent, mod)
    result = [value * scale % mod for value in result]
    return [0] * shift + result

def fps_square_root(series, degree=None, mod=DEFAULT_MOD):
    """Return one formal square root, or None when no root exists. O(N log N)."""
    degree = _fps_formal_power_series_degree(degree, len(series))
    if degree == 0:
        return []
    leading = 0
    limit = min(len(series), degree)
    while leading < limit and series[leading] % mod == 0:
        leading += 1
    if leading == limit:
        return [0] * degree
    if leading & 1:
        return None
    shift = leading >> 1
    needed = degree - shift
    source = [value % mod for value in series[leading:]]
    root = modular_square_root(source[0], mod)
    if root == -1:
        return None
    try:
        inverse_two = pow(2, -1, mod)
    except ValueError as error:
        raise ZeroDivisionError('fps square root requires invertible 2') from error
    inverse_constant = pow(source[0], -1, mod)
    normalized = [value * inverse_constant % mod for value in source]
    terms = _fps_formal_power_series_sparse_terms(normalized, needed, mod, _fps_formal_power_series_SPARSE_POWER_THRESHOLD)
    if terms is not None:
        result = _fps_formal_power_series_fps_power_unit_sparse(needed, inverse_two, terms, mod)
        return [0] * shift + [value * root % mod for value in result]
    result = [root]
    current = 1
    while current < needed:
        target = min(current << 1, needed)
        quotient = fps_multiply(source[:target], fps_inverse(result, target, mod), mod)[:target]
        result.extend([0] * (target - len(result)))
        for index in range(target):
            value = quotient[index] if index < len(quotient) else 0
            result[index] = (result[index] + value) * inverse_two % mod
        current = target
    return [0] * shift + result[:needed]

def fps_taylor_shift(series, shift, mod=DEFAULT_MOD):
    """Return coefficients of ``f(x + shift)``. O(N log N)."""
    size = len(series)
    if size == 0:
        return []
    _fps_formal_power_series_inverses(size, mod)
    factorial = [1] * size
    for index in range(1, size):
        factorial[index] = factorial[index - 1] * index % mod
    try:
        inverse_factorial = [0] * size
        inverse_factorial[-1] = pow(factorial[-1], -1, mod)
    except ValueError as error:
        raise ZeroDivisionError('factorial is not invertible') from error
    for index in range(size - 1, 0, -1):
        inverse_factorial[index - 1] = inverse_factorial[index] * index % mod
    left = [series[index] * factorial[index] % mod for index in range(size)]
    left.reverse()
    right = [0] * size
    power = 1
    shift %= mod
    for index in range(size):
        right[index] = power * inverse_factorial[index] % mod
        power = power * shift % mod
    product = fps_multiply(left, right, mod)
    return [product[size - 1 - index] * inverse_factorial[index] % mod for index in range(size)]

def fps_product(polynomials, mod=DEFAULT_MOD):
    """Multiply many polynomials by repeatedly combining the shortest pair. O(S log S log K)."""
    heap = []
    serial = 0
    for polynomial in polynomials:
        values = [value % mod for value in polynomial]
        if not values:
            return []
        heap.append((len(values), serial, values))
        serial += 1
    if not heap:
        return [1]
    heapify(heap)
    while len(heap) > 1:
        (_, _, first) = heappop(heap)
        (_, _, second) = heappop(heap)
        product = fps_multiply(first, second, mod)
        heappush(heap, (len(product), serial, product))
        serial += 1
    return heap[0][2]
fps_sub = fps_subtract
fps_neg = fps_negate
fps_mul = fps_multiply
fps_diff = fps_derivative
fps_inv = fps_inverse
fps_log = fps_logarithm
fps_exp = fps_exponential
fps_pow = fps_power
fps_sqrt = fps_square_root
fps_eval = fps_evaluate
tayler_shift = fps_taylor_shift
'多項式fから、g(n)=sum(f(i), 0 <= i < n)の係数を求める。'

def polynomial_prefix_sum(polynomial, mod=DEFAULT_MOD, inclusive=False):
    """Return ascending coefficients of the exclusive or inclusive prefix sum."""
    polynomial = fps_shrink(polynomial, mod)
    if not polynomial:
        return []
    size = len(polynomial)
    if size >= mod:
        raise ValueError('polynomial degree plus one must be smaller than mod')
    factorial = [1] * (size + 1)
    for index in range(1, size + 1):
        factorial[index] = factorial[index - 1] * index % mod
    inverse_factorial = [1] * (size + 1)
    inverse_factorial[size] = pow(factorial[size], -1, mod)
    for index in range(size, 0, -1):
        inverse_factorial[index - 1] = inverse_factorial[index] * index % mod
    bernoulli = fps_inverse(inverse_factorial[1:], size, mod)
    weighted = [polynomial[index] * factorial[index] % mod for index in range(size - 1, -1, -1)]
    product = fps_multiply(weighted, bernoulli, mod)
    result = [0] + [product[size - index] * inverse_factorial[index] % mod for index in range(1, size + 1)]
    if inclusive:
        for (index, value) in enumerate(polynomial):
            result[index] = (result[index] + value) % mod
    return result
import sys
read = sys.stdin.buffer.readline
n = int(read())
result = polynomial_prefix_sum(list(map(int, read().split())))
result.extend([0] * (n + 1 - len(result)))
print(*result)
