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
'998244353 固定の高速NTTと係数畳み込み。\n\n`multiply(first, second)` は2つの昇べき順係数列を畳み込み、長さ\n`len(first) + len(second) - 1` の係数列を返す。汎用mod判定、原始根探索、\nCRTを通らず、固定したradix-4の変換表だけを使う。\n'
from array import array
MOD = 998244353
PRIMITIVE_ROOT = 3
MAX_LOG = 23
_convolution_ntt998_IMAG = 911660635
_convolution_ntt998_IIMAG = 86583718
_convolution_ntt998_RATE2 = [0, 911660635, 509520358, 369330050, 332049552, 983190778, 123842337, 238493703, 975955924, 603855026, 856644456, 131300601, 842657263, 730768835, 942482514, 806263778, 151565301, 510815449, 503497456, 743006876, 741047443, 56250497, 867605899, 0]
_convolution_ntt998_IRATE2 = [0, 86583718, 372528824, 373294451, 645684063, 112220581, 692852209, 155456985, 797128860, 90816748, 860285882, 927414960, 354738543, 109331171, 293255632, 535113200, 308540755, 121186627, 608385704, 438932459, 359477183, 824071951, 103369235, 0]
_convolution_ntt998_RATE3 = [0, 372528824, 337190230, 454590761, 816400692, 578227951, 180142363, 83780245, 6597683, 70046822, 623238099, 183021267, 402682409, 631680428, 344509872, 689220186, 365017329, 774342554, 729444058, 102986190, 128751033, 395565204, 0]
_convolution_ntt998_IRATE3 = [0, 509520358, 929031873, 170256584, 839780419, 282974284, 395914482, 444904435, 72135471, 638914820, 66769500, 771127074, 985925487, 262319669, 262341272, 625870173, 768022760, 859816005, 914661783, 430819711, 272774365, 530924681, 0]
_convolution_ntt998_INVERSE_SIZE = {1: 1}

def _convolution_ntt998_check_length(size):
    if size < 1 or size & size - 1:
        raise ValueError('NTT length must be a positive power of two')
    if size > 1 << MAX_LOG:
        raise ValueError('NTT length exceeds 2^23')

def _convolution_ntt998_ntt_plan(size, inverse=False):
    _convolution_ntt998_check_length(size)
    rate2 = _convolution_ntt998_IRATE2 if inverse else _convolution_ntt998_RATE2
    rate3 = _convolution_ntt998_IRATE3 if inverse else _convolution_ntt998_RATE3
    count = max(1, size >> 2)
    first = array('I', [1]) * count
    second = array('I', [1]) * count
    third = array('I', [1]) * count
    rotation = 1
    for block in range(count):
        first[block] = rotation
        second[block] = rotation * rotation % MOD
        third[block] = second[block] * rotation % MOD
        rotation = rotation * rate3[(~block & -~block).bit_length()] % MOD
    count = max(1, size >> 1)
    binary = array('I', [1]) * count
    rotation = 1
    for block in range(count):
        binary[block] = rotation
        rotation = rotation * rate2[(~block & -~block).bit_length()] % MOD
    return (binary, first, second, third)

def _convolution_ntt998_butterfly(values, tables=None):
    """In-place forward radix-4 NTT without coefficient normalization."""
    size = len(values)
    _convolution_ntt998_check_length(size)
    if size == 1:
        values[0] %= MOD
        return values
    if tables is not None:
        (binary, first, second, third) = tables
    height = (size - 1).bit_length()
    level = 0
    mod = MOD
    imag = _convolution_ntt998_IMAG
    rate2 = _convolution_ntt998_RATE2
    rate3 = _convolution_ntt998_RATE3
    while level < height:
        if height - level == 1:
            width = 1 << height - level - 1
            rotation = 1
            for block in range(1 << level):
                if tables is not None:
                    rotation = binary[block]
                offset = block << height - level
                for index in range(width):
                    left = values[offset + index]
                    right = values[offset + index + width] * rotation
                    values[offset + index] = (left + right) % mod
                    values[offset + index + width] = (left - right) % mod
                if tables is None:
                    rotation = rotation * rate2[(~block & -~block).bit_length()] % mod
            level += 1
        else:
            width = 1 << height - level - 2
            rotation = 1
            for block in range(1 << level):
                if tables is None:
                    rotation2 = rotation * rotation % mod
                    rotation3 = rotation2 * rotation % mod
                else:
                    rotation = first[block]
                    rotation2 = second[block]
                    rotation3 = third[block]
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
                if tables is None:
                    rotation = rotation * rate3[(~block & -~block).bit_length()] % mod
            level += 2
    return values

def _convolution_ntt998_butterfly_inv(values, tables=None, keep_bit=0):
    """In-place inverse radix-4 transform without division by the length."""
    size = len(values)
    _convolution_ntt998_check_length(size)
    if size == 1:
        values[0] %= MOD
        return values
    if tables is not None:
        (binary, first, second, third) = tables
    height = (size - 1).bit_length()
    level = height
    mod = MOD
    inverse_imag = _convolution_ntt998_IIMAG
    irate2 = _convolution_ntt998_IRATE2
    irate3 = _convolution_ntt998_IRATE3
    while level:
        if level == 1:
            width = 1 << height - level
            limited = keep_bit and width > keep_bit
            mask = -keep_bit if limited else 0
            count = width >> bool(limited)
            rotation = 1
            for block in range(1 << level - 1):
                if tables is not None:
                    rotation = binary[block]
                offset = block << height - level + 1
                for position in range(count):
                    index = position + (position & mask)
                    left = values[offset + index]
                    right = values[offset + index + width]
                    values[offset + index] = (left + right) % mod
                    values[offset + index + width] = (left - right) * rotation % mod
                if tables is None:
                    rotation = rotation * irate2[(~block & -~block).bit_length()] % mod
            level -= 1
        else:
            width = 1 << height - level
            limited = keep_bit and width > keep_bit
            mask = -keep_bit if limited else 0
            count = width >> bool(limited)
            rotation = 1
            for block in range(1 << level - 2):
                if tables is None:
                    rotation2 = rotation * rotation % mod
                    rotation3 = rotation2 * rotation % mod
                else:
                    rotation = first[block]
                    rotation2 = second[block]
                    rotation3 = third[block]
                offset = block << height - level + 2
                for position in range(count):
                    index = position + (position & mask)
                    value0 = values[offset + index]
                    value1 = values[offset + index + width]
                    value2 = values[offset + index + 2 * width]
                    value3 = values[offset + index + 3 * width]
                    difference = (value2 - value3) * inverse_imag % mod
                    values[offset + index] = (value0 + value1 + value2 + value3) % mod
                    values[offset + index + width] = (value0 - value1 + difference) * rotation % mod
                    values[offset + index + 2 * width] = (value0 + value1 - value2 - value3) * rotation2 % mod
                    values[offset + index + 3 * width] = (value0 - value1 - difference) * rotation3 % mod
                if tables is None:
                    rotation = rotation * irate3[(~block & -~block).bit_length()] % mod
            level -= 2
    return values

def ntt(values):
    """`values`を破壊的に順変換し、同じlistを返す。O(N log N)。"""
    return _convolution_ntt998_butterfly(values)

def _convolution_ntt998__intt(values):
    size = len(values)
    _convolution_ntt998_butterfly_inv(values)
    inverse_size = _convolution_ntt998_INVERSE_SIZE.get(size)
    if inverse_size is None:
        inverse_size = pow(size, MOD - 2, MOD)
        _convolution_ntt998_INVERSE_SIZE[size] = inverse_size
    for index in range(size):
        values[index] = values[index] * inverse_size % MOD
    return values

def intt(values):
    """`values`を破壊的に正規化済み逆変換し、同じlistを返す。O(N log N)。"""
    return _convolution_ntt998__intt(values)

def _convolution_ntt998_multiply_naive(first, second):
    first_size = len(first)
    second_size = len(second)
    if first_size == 0 or second_size == 0:
        return []
    if first_size < second_size:
        (first, second) = (second, first)
        (first_size, second_size) = (second_size, first_size)
    result = [0] * (first_size + second_size - 1)
    mod = MOD
    for (index, left) in enumerate(first):
        left %= mod
        if left:
            for (offset, right) in enumerate(second):
                result[index + offset] += left * right
        if index & 7 == 7:
            start = index
            stop = min(index + second_size, len(result))
            for position in range(start, stop):
                result[position] %= mod
    return [value % mod for value in result]

def _convolution_ntt998_multiply_without_boundary(first, second):
    if min(len(first), len(second)) <= 60:
        return _convolution_ntt998_multiply_naive(first, second)
    first_size = len(first)
    second_size = len(second)
    output_size = first_size + second_size - 1
    size = 1 << (output_size - 1).bit_length()
    _convolution_ntt998_check_length(size)
    left = [value % MOD for value in first]
    left.extend([0] * (size - first_size))
    _convolution_ntt998_butterfly(left)
    if first is second:
        for index in range(size):
            left[index] = left[index] * left[index] % MOD
    else:
        right = [value % MOD for value in second]
        right.extend([0] * (size - second_size))
        _convolution_ntt998_butterfly(right)
        for index in range(size):
            left[index] = left[index] * right[index] % MOD
    _convolution_ntt998_butterfly_inv(left)
    inverse_size = _convolution_ntt998_INVERSE_SIZE.get(size)
    if inverse_size is None:
        inverse_size = pow(size, MOD - 2, MOD)
        _convolution_ntt998_INVERSE_SIZE[size] = inverse_size
    for index in range(output_size):
        left[index] = left[index] * inverse_size % MOD
    del left[output_size:]
    return left

def multiply(first, second):
    """2つの係数列の積を長さ`len(first)+len(second)-1`で返す。O(N log N)。"""
    first_size = len(first)
    second_size = len(second)
    if first_size == 0 or second_size == 0:
        return []
    if min(first_size, second_size) <= 60:
        return _convolution_ntt998_multiply_naive(first, second)
    if first_size < second_size:
        (first, second) = (second, first)
        (first_size, second_size) = (second_size, first_size)
    output_size = first_size + second_size - 1
    lower_power = 1 << output_size.bit_length() - 1
    boundary_excess = output_size - lower_power
    if 0 < boundary_excess <= 128 and (boundary_excess * second_size <= 2 * lower_power or lower_power == 1 << 23):
        prefix = _convolution_ntt998_multiply_without_boundary(first[:-boundary_excess], second)
        prefix.extend([0] * boundary_excess)
        tail_start = first_size - boundary_excess
        for index in range(tail_start, first_size):
            left = first[index] % MOD
            if left:
                for (offset, right) in enumerate(second):
                    prefix[index + offset] += left * right
        for index in range(tail_start, output_size):
            prefix[index] %= MOD
        return prefix
    return _convolution_ntt998_multiply_without_boundary(first, second)

def square(series):
    """係数列の二乗を長さ`2*len(series)-1`で返す。O(N log N)。"""
    size = len(series)
    if size == 0:
        return []
    if size <= 60:
        result = [0] * (2 * size - 1)
        for (index, left) in enumerate(series):
            left %= MOD
            result[index << 1] += left * left
            for offset in range(index + 1, size):
                result[index + offset] += 2 * left * series[offset]
        return [value % MOD for value in result]
    return multiply(series, series)
'998244353上の形式的冪級数を昇べき順の係数listで計算する。\n\n`a[i]`は$x^i$の係数を表す。inv・log・exp・pow・sqrt、微分・積分、\n多項式除算、Taylor shift、一括積を固定modのradix-4 NTTで計算する。\n入力listは変更せず、新しい係数listを返す。\n'
from heapq import heapify as _fps998_fps_heapify, heappop as _fps998_fps_heappop, heappush as _fps998_fps_heappush
_fps998_fps_INVERSES = [0, 1]
_fps998_fps_SPARSE_INV_THRESHOLD = 160
_fps998_fps_SPARSE_DIV_THRESHOLD = 200
_fps998_fps_SPARSE_LOG_THRESHOLD = 200
_fps998_fps_SPARSE_EXP_THRESHOLD = 320
_fps998_fps_SPARSE_POWER_THRESHOLD = 32

def _fps998_fps_mod_sqrt(value):
    value %= MOD
    if value < 2:
        return value
    if pow(value, MOD - 1 >> 1, MOD) != 1:
        return -1
    odd = MOD - 1
    exponent = 0
    while odd & 1 == 0:
        odd >>= 1
        exponent += 1
    nonresidue = 3
    root = pow(value, odd + 1 >> 1, MOD)
    remainder = pow(value, odd, MOD)
    generator = pow(nonresidue, odd, MOD)
    level = exponent
    while remainder != 1:
        position = 1
        squared = remainder * remainder % MOD
        while position < level and squared != 1:
            squared = squared * squared % MOD
            position += 1
        if position == level:
            return -1
        adjustment = pow(generator, 1 << level - position - 1, MOD)
        root = root * adjustment % MOD
        adjustment = adjustment * adjustment % MOD
        remainder = remainder * adjustment % MOD
        generator = adjustment
        level = position
    return min(root, MOD - root)

def _fps998_fps_degree(degree, default):
    if degree is None:
        return default
    if degree < 0:
        raise ValueError('degree must be nonnegative')
    return degree

def _fps998_fps_inverses(size):
    if size >= MOD:
        raise ValueError('formal integration requires degree < 998244353')
    values = _fps998_fps_INVERSES
    for index in range(len(values), size + 1):
        values.append(-values[MOD % index] * (MOD // index) % MOD)
    return values

def _fps998_fps_sparse_terms(series, degree, threshold):
    terms = []
    for index in range(1, min(len(series), degree)):
        value = series[index] % MOD
        if value:
            terms.append((index, value))
            if len(terms) > threshold:
                return None
    return terms

def _fps998_fps_fps_inv_sparse(series, degree, first_inverse, terms):
    result = [0] * degree
    result[0] = first_inverse
    for index in range(1, degree):
        total = 0
        for (offset, coefficient) in terms:
            if offset > index:
                break
            total += coefficient * result[index - offset]
        result[index] = -total * first_inverse % MOD
    return result

def _fps998_fps_fps_div_sparse(numerator, degree, first_inverse, terms):
    result = [0] * degree
    for index in range(degree):
        total = numerator[index] % MOD if index < len(numerator) else 0
        for (offset, coefficient) in terms:
            if offset > index:
                break
            total -= coefficient * result[index - offset]
        result[index] = total * first_inverse % MOD
    return result

def _fps998_fps_fps_log_sparse(series, degree, terms):
    inverse = _fps998_fps_inverses(degree)
    derivative = [0] * max(0, degree - 1)
    for index in range(degree - 1):
        total = (index + 1) * series[index + 1] % MOD if index + 1 < len(series) else 0
        for (offset, coefficient) in terms:
            if offset > index:
                break
            total -= coefficient * derivative[index - offset]
        derivative[index] = total % MOD
    return [0] + [value * inverse[index] % MOD for (index, value) in enumerate(derivative, 1)]

def _fps998_fps_fps_exp_sparse(degree, terms):
    inverse = _fps998_fps_inverses(degree)
    terms = [(offset, offset * coefficient % MOD) for (offset, coefficient) in terms]
    result = [0] * degree
    result[0] = 1
    for index in range(1, degree):
        total = 0
        for (offset, coefficient) in terms:
            if offset > index:
                break
            total += coefficient * result[index - offset]
        result[index] = total % MOD * inverse[index] % MOD
    return result

def _fps998_fps_fps_power_unit_sparse(degree, exponent, terms):
    inverse = _fps998_fps_inverses(degree)
    result = [0] * degree
    result[0] = 1
    factor = (exponent + 1) % MOD
    terms = [(offset, coefficient, factor * offset * coefficient % MOD) for (offset, coefficient) in terms]
    for index in range(1, degree):
        total = 0
        for (offset, coefficient, weighted) in terms:
            if offset > index:
                break
            total += (weighted - index * coefficient) % MOD * result[index - offset]
        result[index] = total % MOD * inverse[index] % MOD
    return result

def _fps998_fps_shrink(series):
    """係数をmodで正規化し、末尾の0を除いた新しいlistを返す。O(N)。"""
    result = [value % MOD for value in series]
    while result and result[-1] == 0:
        result.pop()
    return result

def _fps998_fps_fps_add(first, second):
    """2つのFPSを係数ごとに加え、長い方と同じ長さのlistを返す。O(N)。"""
    size = max(len(first), len(second))
    result = [0] * size
    common = min(len(first), len(second))
    mod = MOD
    for index in range(common):
        result[index] = (first[index] + second[index]) % mod
    for index in range(common, len(first)):
        result[index] = first[index] % mod
    for index in range(common, len(second)):
        result[index] = second[index] % mod
    return result

def _fps998_fps_fps_sub(first, second):
    """`first-second`の係数列を長い方と同じ長さで返す。O(N)。"""
    size = max(len(first), len(second))
    result = [0] * size
    common = min(len(first), len(second))
    mod = MOD
    for index in range(common):
        result[index] = (first[index] - second[index]) % mod
    for index in range(common, len(first)):
        result[index] = first[index] % mod
    for index in range(common, len(second)):
        result[index] = -second[index] % mod
    return result

def _fps998_fps_fps_neg(series):
    """各係数の加法逆元を同じ長さのlistで返す。O(N)。"""
    return [-value % MOD for value in series]

def _fps998_fps_fps_diff(series):
    """形式微分の係数を昇べき順で返す。O(N)。"""
    mod = MOD
    return [index * series[index] % mod for index in range(1, len(series))]

def _fps998_fps_fps_integral(series):
    """定数項を0とした形式積分の係数を昇べき順で返す。O(N)。"""
    inverse = _fps998_fps_inverses(len(series))
    mod = MOD
    result = [0] * (len(series) + 1)
    for (index, value) in enumerate(series, 1):
        result[index] = value * inverse[index] % mod
    return result

def _fps998_fps_fps_eval(series, value):
    """FPSを多項式とみなし`value`へ代入した値を返す。O(N)。"""
    result = 0
    value %= MOD
    mod = MOD
    for coefficient in reversed(series):
        result = (result * value + coefficient) % mod
    return result

def _fps998_fps_inverse_step(series, result, current, target):
    size = current << 1
    mod = MOD
    left = [value % mod for value in series[:target]]
    left.extend([0] * (size - len(left)))
    right = result + [0] * (size - current)
    _convolution_ntt998_butterfly(left)
    _convolution_ntt998_butterfly(right)
    for index in range(size):
        left[index] = left[index] * right[index] % mod
    _convolution_ntt998__intt(left)
    for index in range(current):
        left[index] = 0
    for index in range(current, target):
        left[index] = -left[index] % mod
    for index in range(target, size):
        left[index] = 0
    _convolution_ntt998_butterfly(left)
    for index in range(size):
        left[index] = left[index] * right[index] % mod
    _convolution_ntt998__intt(left)
    result.extend(left[current:target])

def _fps998_fps_inverse_step_from_frequency(series_frequency, inverse_frequency, result, current):
    """Extend ``result = 1 / series`` from ``current`` to ``2 * current``.

    ``series_frequency`` is the length ``2 * current`` transform of the
    series.  ``inverse_frequency`` is the length ``current`` transform of
    the already known inverse.  Reusing both transforms is useful when an
    outer Newton iteration already needs them (notably FPS square root).
    """
    half = current
    size = half << 1
    error = [series_frequency[index] * inverse_frequency[index] % MOD for index in range(half)]
    _convolution_ntt998__intt(error)
    error = error[half >> 1:] + [0] * (half >> 1)
    _convolution_ntt998_butterfly(error)
    for index in range(half):
        error[index] = error[index] * inverse_frequency[index] % MOD
    _convolution_ntt998__intt(error)
    result.extend([-value % MOD for value in error[:half >> 1]])

def _fps998_fps_fps_inv(series, degree=None):
    """$1/f(x)\\bmod x^{degree}$の係数を`degree`個返す。O(N log N)。"""
    degree = _fps998_fps_degree(degree, len(series))
    if degree == 0:
        return []
    if not series or series[0] % MOD == 0:
        raise ZeroDivisionError('fps inverse requires nonzero constant coefficient')
    first_inverse = pow(series[0] % MOD, MOD - 2, MOD)
    terms = _fps998_fps_sparse_terms(series, degree, _fps998_fps_SPARSE_INV_THRESHOLD)
    if terms is not None:
        return _fps998_fps_fps_inv_sparse(series, degree, first_inverse, terms)
    result = [first_inverse]
    current = 1
    while current < degree:
        target = min(current << 1, degree)
        _convolution_ntt998_check_length(current << 1)
        _fps998_fps_inverse_step(series, result, current, target)
        current = target
    return result

def _fps998_fps_fps_div(numerator, denominator, degree=None):
    """Return ``numerator / denominator mod x^degree``. O(N log N)."""
    degree = _fps998_fps_degree(degree, len(numerator))
    if degree == 0:
        return []
    if not denominator or denominator[0] % MOD == 0:
        raise ZeroDivisionError('fps division requires nonzero denominator constant')
    first_inverse = pow(denominator[0] % MOD, MOD - 2, MOD)
    terms = _fps998_fps_sparse_terms(denominator, degree, _fps998_fps_SPARSE_DIV_THRESHOLD)
    if terms is not None:
        return _fps998_fps_fps_div_sparse(numerator, degree, first_inverse, terms)
    inverse = _fps998_fps_fps_inv(denominator, degree)
    result = multiply(numerator[:degree], inverse)[:degree]
    result.extend([0] * (degree - len(result)))
    return result

def _fps998_fps_fps_log(series, degree=None):
    """$\\log f(x)\\bmod x^{degree}$を返す。`f[0]`は1。O(N log N)。"""
    degree = _fps998_fps_degree(degree, len(series))
    if degree == 0:
        return []
    if not series or series[0] % MOD != 1:
        raise ValueError('fps logarithm requires constant coefficient 1')
    terms = _fps998_fps_sparse_terms(series, degree, _fps998_fps_SPARSE_LOG_THRESHOLD)
    if terms is not None:
        return _fps998_fps_fps_log_sparse(series, degree, terms)
    product = multiply(_fps998_fps_fps_diff(series), _fps998_fps_fps_inv(series, degree))
    result = _fps998_fps_fps_integral(product[:degree - 1])
    result.extend([0] * (degree - len(result)))
    return result

def _fps998_fps_fps_exp_ntt(series, degree):
    mod = MOD
    b = [1, series[1] % mod if len(series) > 1 else 0]
    c = [1]
    z2 = [1, 1]
    inverse = [0, 1]
    size = 2
    while size < degree:
        doubled = size << 1
        y = b + [0] * size
        _convolution_ntt998_butterfly(y)
        z1 = z2
        z = [y[index] * z1[index] % mod for index in range(size)]
        _convolution_ntt998__intt(z)
        for index in range(size >> 1):
            z[index] = 0
        _convolution_ntt998_butterfly(z)
        for index in range(size):
            z[index] = -z[index] * z1[index] % mod
        _convolution_ntt998__intt(z)
        c.extend(z[size >> 1:])
        z2 = c + [0] * size
        _convolution_ntt998_butterfly(z2)
        source_size = min(len(series), size)
        x = [series[index] % mod for index in range(source_size)]
        x.extend([0] * (size - source_size))
        x = _fps998_fps_fps_diff(x)
        x.append(0)
        _convolution_ntt998_butterfly(x)
        for index in range(size):
            x[index] = x[index] * y[index] % mod
        _convolution_ntt998__intt(x)
        for index in range(1, len(b)):
            x[index - 1] = (x[index - 1] - index * b[index]) % mod
        x.extend([0] * size)
        for index in range(size - 1):
            (x[size + index], x[index]) = (x[index], 0)
        _convolution_ntt998_butterfly(x)
        for index in range(doubled):
            x[index] = x[index] * z2[index] % mod
        _convolution_ntt998__intt(x)
        x.pop()
        for index in range(len(inverse), len(x) + 1):
            inverse.append(-inverse[mod % index] * (mod // index) % mod)
        x = [0] + [value * inverse[index + 1] % mod for (index, value) in enumerate(x)]
        for index in range(size):
            x[index] = 0
        for index in range(size, min(len(series), doubled)):
            x[index] = (x[index] + series[index]) % mod
        _convolution_ntt998_butterfly(x)
        for index in range(doubled):
            x[index] = x[index] * y[index] % mod
        _convolution_ntt998__intt(x)
        b.extend(x[size:])
        size = doubled
    return b[:degree]

def _fps998_fps_fps_exp(series, degree=None):
    """$\\exp f(x)\\bmod x^{degree}$を返す。`f[0]`は0。O(N log N)。"""
    degree = _fps998_fps_degree(degree, len(series))
    if degree == 0:
        return []
    if series and series[0] % MOD:
        raise ValueError('fps exponential requires constant coefficient 0')
    terms = _fps998_fps_sparse_terms(series, degree, _fps998_fps_SPARSE_EXP_THRESHOLD)
    if terms is not None:
        return _fps998_fps_fps_exp_sparse(degree, terms)
    _convolution_ntt998_check_length(1 << (degree - 1).bit_length())
    if degree == 1:
        return [1]
    return _fps998_fps_fps_exp_ntt(series, degree)

def _fps998_fps_fps_pow(series, exponent, degree=None):
    """$f(x)^{exponent}\\bmod x^{degree}$を係数`degree`個で返す。O(N log N)。"""
    degree = _fps998_fps_degree(degree, len(series))
    if degree == 0:
        return []
    if exponent == 0:
        return [1] + [0] * (degree - 1)
    leading = 0
    while leading < len(series) and series[leading] % MOD == 0:
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
    coefficient = series[leading] % MOD
    inverse_coefficient = pow(coefficient, MOD - 2, MOD)
    needed = degree - shift
    normalized = [value * inverse_coefficient % MOD for value in series[leading:]]
    terms = _fps998_fps_sparse_terms(normalized, needed, _fps998_fps_SPARSE_POWER_THRESHOLD)
    if terms is not None:
        result = _fps998_fps_fps_power_unit_sparse(needed, exponent, terms)
    else:
        logarithm = _fps998_fps_fps_log(normalized, needed)
        for index in range(needed):
            logarithm[index] = logarithm[index] * exponent % MOD
        result = _fps998_fps_fps_exp(logarithm, needed)
    scale = pow(coefficient, exponent, MOD)
    return [0] * shift + [value * scale % MOD for value in result]

def _fps998_fps_fps_sqrt(series, degree=None):
    """$g(x)^2=f(x)\\bmod x^{degree}$となる係数列を返し、なければ`None`。O(N log N)。"""
    degree = _fps998_fps_degree(degree, len(series))
    if degree == 0:
        return []
    leading = 0
    limit = min(len(series), degree)
    while leading < limit and series[leading] % MOD == 0:
        leading += 1
    if leading == limit:
        return [0] * degree
    if leading & 1:
        return None
    shift = leading >> 1
    needed = degree - shift
    source = [value % MOD for value in series[leading:]]
    root = _fps998_fps_mod_sqrt(source[0])
    if root == -1:
        return None
    inverse_constant = pow(source[0], MOD - 2, MOD)
    normalized = [value * inverse_constant % MOD for value in source]
    terms = _fps998_fps_sparse_terms(normalized, needed, _fps998_fps_SPARSE_POWER_THRESHOLD)
    if terms is not None:
        result = _fps998_fps_fps_power_unit_sparse(needed, MOD + 1 >> 1, terms)
        return [0] * shift + [value * root % MOD for value in result]
    inverse_two = MOD + 1 >> 1
    result = [root]
    inverse_result = [pow(root, MOD - 2, MOD)]
    inverse_frequency = None
    current = 1
    while current < needed:
        size = current << 1
        _convolution_ntt998_check_length(size)
        result_frequency = result + [0] * current
        _convolution_ntt998_butterfly(result_frequency)
        if current > 1:
            _fps998_fps_inverse_step_from_frequency(result_frequency, inverse_frequency, inverse_result, current)
        inverse_frequency = inverse_result + [0] * current
        _convolution_ntt998_butterfly(inverse_frequency)
        source_frequency = source[:size]
        source_frequency.extend([0] * (size - len(source_frequency)))
        _convolution_ntt998_butterfly(source_frequency)
        for index in range(size):
            value = result_frequency[index]
            source_frequency[index] = (source_frequency[index] - value * value) * inverse_frequency[index] % MOD
        _convolution_ntt998__intt(source_frequency)
        result.extend((value * inverse_two % MOD for value in source_frequency[current:size]))
        current = size
    return [0] * shift + result[:needed]

def taylor_shift(series, shift):
    """$f(x+shift)$の係数を`f`と同じ長さのlistで返す。O(N log N)。"""
    size = len(series)
    if size == 0:
        return []
    factorial = [1] * size
    for index in range(1, size):
        factorial[index] = factorial[index - 1] * index % MOD
    inverse_factorial = [0] * size
    inverse_factorial[-1] = pow(factorial[-1], MOD - 2, MOD)
    for index in range(size - 1, 0, -1):
        inverse_factorial[index - 1] = inverse_factorial[index] * index % MOD
    left = [series[index] * factorial[index] % MOD for index in range(size)]
    left.reverse()
    right = [0] * size
    power = 1
    shift %= MOD
    for index in range(size):
        right[index] = power * inverse_factorial[index] % MOD
        power = power * shift % MOD
    product = multiply(left, right)
    return [product[size - 1 - index] * inverse_factorial[index] % MOD for index in range(size)]

def _fps998_fps_fps_product(polynomials):
    """複数の多項式をすべて掛けた係数列を返す。O(S log S log K)。"""
    heap = []
    serial = 0
    for polynomial in polynomials:
        values = [value % MOD for value in polynomial]
        if not values:
            return []
        heap.append((len(values), serial, values))
        serial += 1
    if not heap:
        return [1]
    if all((item[0] == heap[0][0] for item in heap)):
        level = [item[2] for item in heap]
        while len(level) > 1:
            next_level = []
            paired = len(level) & ~1
            for index in range(0, paired, 2):
                next_level.append(multiply(level[index], level[index + 1]))
            if paired < len(level):
                next_level.append(level[-1])
            level = next_level
        return level[0]
    _fps998_fps_heapify(heap)
    while len(heap) > 1:
        (_, _, first) = _fps998_fps_heappop(heap)
        (_, _, second) = _fps998_fps_heappop(heap)
        product = multiply(first, second)
        _fps998_fps_heappush(heap, (len(product), serial, product))
        serial += 1
    return heap[0][2]
'第一種・第二種Stirling数の行または列を生成する。'

def _combinatorial_series_stirling_numbers_factorials(size, mod):
    if size >= mod:
        raise ValueError('series degree must be smaller than mod')
    factorial = [1] * (size + 1)
    for index in range(1, size + 1):
        factorial[index] = factorial[index - 1] * index % mod
    inverse_factorial = [1] * (size + 1)
    if size:
        inverse_factorial[-1] = pow(factorial[-1], -1, mod)
        for index in range(size, 0, -1):
            inverse_factorial[index - 1] = inverse_factorial[index] * index % mod
    return (factorial, inverse_factorial)

def stirling_first_row(order, mod=DEFAULT_MOD, signed=False):
    """Coefficients of rising factorial x(x+1)...(x+order-1)."""
    if order < 0:
        raise ValueError('order must be nonnegative')
    if order == 0:
        return [1]
    polynomial = [0, 1]
    for bit in range(order.bit_length() - 2, -1, -1):
        current = order >> bit
        shifted = fps_taylor_shift(polynomial, current >> 1, mod)
        polynomial = fps_multiply(polynomial, shifted, mod)
        if current & 1:
            result = [0] * (len(polynomial) + 1)
            scale = current - 1
            for (index, value) in enumerate(polynomial):
                result[index] = (result[index] + value * scale) % mod
                result[index + 1] = (result[index + 1] + value) % mod
            polynomial = result
    if signed:
        for index in range(order + 1):
            if order - index & 1:
                polynomial[index] = -polynomial[index] % mod
    return polynomial

def stirling_second_row(order, mod=DEFAULT_MOD):
    """Return S(order, 0), ..., S(order, order)."""
    if order < 0:
        raise ValueError('order must be nonnegative')
    (factorial, inverse_factorial) = _combinatorial_series_stirling_numbers_factorials(order, mod)
    powers = [pow(index, order, mod) * inverse_factorial[index] % mod for index in range(order + 1)]
    signs = [(-inverse_factorial[index] if index & 1 else inverse_factorial[index]) % mod for index in range(order + 1)]
    return fps_multiply(powers, signs, mod)[:order + 1]

def stirling_first_column(column, upper, mod=DEFAULT_MOD):
    """Unsigned first-kind Stirling numbers s(n, column), column <= n <= upper."""
    if column < 0 or upper < 0:
        raise ValueError('indices must be nonnegative')
    if upper < column:
        return []
    (factorial, inverse_factorial) = _combinatorial_series_stirling_numbers_factorials(upper, mod)
    if column == 0:
        return [1] + [0] * upper
    if column == 1:
        return [0] + factorial[:upper]
    if column == 2:
        result = [0] * (upper + 1)
        harmonic = 0
        for index in range(2, upper + 1):
            harmonic = (harmonic + factorial[index - 2] * inverse_factorial[index - 1]) % mod
            result[index] = factorial[index - 1] * harmonic % mod
        return result
    needed = upper - column + 1
    logarithm = [0] + [factorial[index - 1] * inverse_factorial[index] % mod for index in range(1, needed + 1)]
    if mod == DEFAULT_MOD:
        values = _fps998_fps_fps_pow(logarithm, column, upper + 1)
    else:
        values = fps_power(logarithm, column, upper + 1, mod)
    scale = inverse_factorial[column]
    result = [0] * (upper + 1)
    for index in range(column, upper + 1):
        result[index] = values[index] * scale % mod * factorial[index] % mod
    return result

def stirling_second_column(column, upper, mod=DEFAULT_MOD):
    """Second-kind Stirling numbers S(n, column), column <= n <= upper."""
    if column < 0 or upper < 0:
        raise ValueError('indices must be nonnegative')
    if upper < column:
        return []
    (factorial, inverse_factorial) = _combinatorial_series_stirling_numbers_factorials(upper, mod)
    if column == 0:
        return [1] + [0] * upper
    if column == 1:
        return [0] + [1] * upper
    if column == 2:
        result = [0] * (upper + 1)
        value = 0
        for index in range(2, upper + 1):
            value = (2 * value + 1) % mod
            result[index] = value
        return result
    exponential_minus_one = [0] + inverse_factorial[1:upper - column + 2]
    if mod == DEFAULT_MOD:
        values = _fps998_fps_fps_pow(exponential_minus_one, column, upper + 1)
    else:
        values = fps_power(exponential_minus_one, column, upper + 1, mod)
    scale = inverse_factorial[column]
    result = [0] * (upper + 1)
    for index in range(column, upper + 1):
        result[index] = values[index] * scale % mod * factorial[index] % mod
    return result
import sys

def main():
    (n, k) = map(int, sys.stdin.buffer.readline().split())
    result = stirling_first_column(k, n)
    for i in range(k + 1, n + 1, 2):
        result[i] = -result[i] % 998244353
    sys.stdout.write(' '.join(map(str, result[k:])) + '\n')
if __name__ == '__main__':
    main()
