"""998244353 固定の高速NTTと係数畳み込み。

`multiply(first, second)` は2つの昇べき順係数列を畳み込み、長さ
`len(first) + len(second) - 1` の係数列を返す。汎用mod判定、原始根探索、
CRTを通らず、固定したradix-4の変換表だけを使う。
"""
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
'符号付き10進・16進文字列を、浮動小数点を使わず高速に乗算する。'

def _number_theory_big_integer_multiplication_parts(value, radix):
    negative = value.startswith('-')
    if value[:1] in ('+', '-'):
        value = value[1:]
    if not value or not value.isascii():
        raise ValueError('expected a signed integer string')
    if radix == 10:
        valid = value.isdecimal()
    else:
        valid = not value.strip('0123456789abcdefABCDEF')
    if not valid:
        raise ValueError('invalid digit')
    return (negative, value.lstrip('0') or '0')

def _number_theory_big_integer_multiplication_product(first, second, radix, width):
    if first == '0' or second == '0':
        return '0'
    if len(first) + len(second) <= 512:
        value = int(first, radix) * int(second, radix)
        return str(value) if radix == 10 else format(value, 'X')
    base = radix ** width
    a = [int(first[max(0, i - width):i], radix) for i in range(len(first), 0, -width)]
    b = a if first == second else [int(second[max(0, i - width):i], radix) for i in range(len(second), 0, -width)]
    length = len(a) + len(b) - 1
    if min(len(a), len(b)) <= 32:
        if len(a) > len(b):
            (a, b) = (b, a)
        result = [0] * length
        for (i, value) in enumerate(a):
            for (j, other) in enumerate(b):
                result[i + j] += value * other
    else:
        if length > 1 << 23:
            raise ValueError('convolution length exceeds 2^23')
        result = multiply(a, b)
        other = convolution_ntt(a, b, 469762049, 3)
        inverse = pow(998244353, -1, 469762049)
        for i in range(length):
            result[i] += 998244353 * ((other[i] - result[i]) * inverse % 469762049)
    carry = 0
    for i in range(length):
        (carry, result[i]) = divmod(result[i] + carry, base)
    while carry:
        (carry, value) = divmod(carry, base)
        result.append(value)
    while result and result[-1] == 0:
        result.pop()
    if radix == 10:
        return str(result[-1]) + ''.join((str(value).zfill(width) for value in reversed(result[:-1])))
    return format(result[-1], 'X') + ''.join((format(value, 'X').zfill(width) for value in reversed(result[:-1])))

def multiply_decimal(first, second):
    """符号付き10進文字列同士の積を、先頭0のない10進文字列で返す。O(N log N)。"""
    (negative, first) = _number_theory_big_integer_multiplication_parts(first, 10)
    (other_negative, second) = _number_theory_big_integer_multiplication_parts(second, 10)
    result = _number_theory_big_integer_multiplication_product(first, second, 10, 5)
    return '-' + result if negative != other_negative and result != '0' else result

def multiply_hex(first, second):
    """符号付き16進文字列同士の積を、大文字・先頭0なしの16進文字列で返す。O(N log N)。"""
    (negative, first) = _number_theory_big_integer_multiplication_parts(first, 16)
    (other_negative, second) = _number_theory_big_integer_multiplication_parts(second, 16)
    result = _number_theory_big_integer_multiplication_product(first.upper(), second.upper(), 16, 4)
    return '-' + result if negative != other_negative and result != '0' else result
import sys

def main():
    read = sys.stdin.readline
    count = int(read())
    answer = []
    for _ in range(count):
        (first, second) = read().split()
        answer.append(multiply_hex(first, second))
    sys.stdout.write('\n'.join(answer) + '\n')
if __name__ == '__main__':
    main()
