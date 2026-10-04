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
'多変数多項式を指定shapeの係数配列として乗算する。'
DEFAULT_MOD = 998244353

def multivariate_multiplication(first, second, base, mod=DEFAULT_MOD):
    """Multiply dense multivariate polynomials truncated by each degree base."""
    if len(first) != len(second):
        raise ValueError('input lengths differ')
    size = 1
    for radix in base:
        if radix <= 0:
            raise ValueError('radices must be positive')
        size *= radix
    if len(first) != size:
        raise ValueError('input length must equal product(base)')
    return _convolution_multivariate_multiplication_multiply_prefix(first, second, base, mod, size)

def _convolution_multivariate_multiplication_multiply_prefix(first, second, base, mod, size):
    base = tuple((radix for radix in base if radix > 1))
    first = first[:size]
    second = second[:size]
    if not first or not second:
        return [0] * size
    dimensions = len(base)
    if dimensions == 0:
        return [first[0] * second[0] % mod]
    width = min(base[0], size)
    packed_size = len(first) + len(second) - 1 + ((len(first) - 1) // width + (len(second) - 1) // width) * (width - 1)
    if dimensions <= 2 and (mod != DEFAULT_MOD or packed_size <= 1 << 23):
        stride = 2 * width - 1
        left = [0] * (len(first) + (len(first) - 1) // width * (width - 1))
        right = [0] * (len(second) + (len(second) - 1) // width * (width - 1))
        for start in range(0, len(first), width):
            position = start // width * stride
            left[position:position + min(width, len(first) - start)] = first[start:start + width]
        for start in range(0, len(second), width):
            position = start // width * stride
            right[position:position + min(width, len(second) - start)] = second[start:start + width]
        product = multiply(left, right) if mod == DEFAULT_MOD else convolution(left, right, mod)
        result = [0] * size
        for start in range(0, size, width):
            position = start // width * stride
            count = min(width, size - start, max(0, len(product) - position))
            result[start:start + count] = product[position:position + count]
        return result
    transform_size = 1
    while transform_size < size * 2:
        transform_size <<= 1
    chi = [0] * size
    for index in range(size):
        value = index
        total = 0
        for axis in range(dimensions - 1):
            value //= base[axis]
            total += value
        chi[index] = total % dimensions
    left = [[0] * transform_size for _ in range(dimensions)]
    right = [[0] * transform_size for _ in range(dimensions)]
    for (index, value) in enumerate(first):
        left[chi[index]][index] = value % mod
    for (index, value) in enumerate(second):
        right[chi[index]][index] = value % mod
    ntt = get_ntt(mod)
    for row in left:
        ntt.butterfly(row)
    for row in right:
        ntt.butterfly(row)
    scratch = [0] * dimensions
    for frequency in range(transform_size):
        for group in range(dimensions):
            scratch[group] = 0
        for i in range(dimensions):
            a = left[i][frequency]
            if a:
                for j in range(dimensions):
                    scratch[(i + j) % dimensions] += a * right[j][frequency]
        for group in range(dimensions):
            left[group][frequency] = scratch[group] % mod
    for row in left:
        ntt.butterfly_inv(row)
    return [left[chi[index]][index] for index in range(size)]
'各変数の次数を打ち切った係数列で、積・逆数・log・exp・整数冪を求める。'

def _fps_multivariate_fps_inverse_prefix(series, base, mod, size):
    if mod == DEFAULT_MOD and len(base) == 2 and (min(base) > 1) and (256 <= size <= 1 << 23):
        return _fps_multivariate_fps_inverse_2d(series, base[0], size)
    result = [pow(series[0], -1, mod)]
    while len(result) < size:
        previous = len(result)
        target = min(2 * previous, size)
        error = _convolution_multivariate_multiplication_multiply_prefix(series, result, base, mod, target)
        error[:previous] = [0] * previous
        error = _convolution_multivariate_multiplication_multiply_prefix(error, result, base, mod, target)
        result.extend((-value % mod for value in error[previous:]))
    return result

def _fps_multivariate_fps_inverse_2d(series, width, size):
    mod = DEFAULT_MOD
    result = [pow(series[0], -1, mod)]
    while len(result) < size:
        degree = len(result)
        length = 2 * degree
        left = [[0] * length for _ in range(2)]
        right = [[0] * length for _ in range(2)]
        for (i, value) in enumerate(series[:length]):
            left[i // width & 1][i] = value
        for (i, value) in enumerate(result):
            right[i // width & 1][i] = value
        for row in left + right:
            ntt(row)
        (a, b) = left
        (c, d) = right
        high = [[(a[i] * c[i] + b[i] * d[i]) % mod for i in range(length)], [(a[i] * d[i] + b[i] * c[i]) % mod for i in range(length)]]
        for row in high:
            intt(row)
        left = [[0] * length for _ in range(2)]
        for i in range(degree, min(length, size)):
            color = i // width & 1
            left[color][i] = high[color][i]
        for row in left:
            ntt(row)
        (a, b) = left
        high = [[(a[i] * c[i] + b[i] * d[i]) % mod for i in range(length)], [(a[i] * d[i] + b[i] * c[i]) % mod for i in range(length)]]
        for row in high:
            intt(row)
        result.extend((-high[i // width & 1][i] % mod for i in range(degree, min(length, size))))
    return result

def _fps_multivariate_fps_inverses(size, mod):
    result = [1] * size
    for index in range(2, size):
        result[index] = result[index - 1] * index % mod
    inverse = pow(result[-1], -1, mod)
    for index in range(size - 1, 0, -1):
        (result[index], inverse) = (inverse * result[index - 1] % mod, inverse * index % mod)
    result[0] = 0
    return result

def _fps_multivariate_fps_log_prefix(series, base, mod, size, inverses):
    derivative = [index * value % mod for (index, value) in enumerate(series[:size])]
    inverse = _fps_multivariate_fps_inverse_prefix(series, base, mod, size)
    result = _convolution_multivariate_multiplication_multiply_prefix(derivative, inverse, base, mod, size)
    for index in range(size):
        result[index] = result[index] * inverses[index] % mod
    return result

def _fps_multivariate_fps_exp_prefix(series, base, mod, size):
    inverses = _fps_multivariate_fps_inverses(size, mod)
    result = [1]
    while len(result) < size:
        target = min(2 * len(result), size)
        logarithm = _fps_multivariate_fps_log_prefix(result, base, mod, target, inverses)
        correction = [(series[index] - logarithm[index]) % mod for index in range(target)]
        correction[0] += 1
        result = _convolution_multivariate_multiplication_multiply_prefix(result, correction, base, mod, target)
    return result

def _fps_multivariate_fps_sparse_2d(series, base, mod, exponent=None, logarithm=False):
    if len(base) != 2 or mod != DEFAULT_MOD or len(series) >= mod:
        return None
    width = base[0]
    terms = []
    limit = min(64 if exponent == -1 else 128, max(16, len(series) // 8))
    inverse_constant = pow(series[0], -1, mod) if exponent is not None else 1
    for offset in range(1, len(series)):
        coefficient = series[offset] * inverse_constant % mod
        if coefficient:
            terms.append((offset, offset % width, coefficient))
            if len(terms) > limit:
                return None
    inverses = _fps_multivariate_fps_inverses(len(series), mod)
    result = [0] * len(series)
    result[0] = 1 if exponent is None else pow(series[0], exponent, mod)
    if logarithm:
        result[0] = 0
        for index in range(1, len(series)):
            x = index % width
            total = index * series[index] % mod
            for (offset, column, coefficient) in terms:
                if offset >= index:
                    break
                if column <= x:
                    total -= coefficient * result[index - offset]
            result[index] = total % mod
        for index in range(1, len(series)):
            result[index] = result[index] * inverses[index] % mod
    elif exponent is None:
        terms = [(offset, x, offset * coefficient % mod) for (offset, x, coefficient) in terms]
        for index in range(1, len(series)):
            x = index % width
            total = 0
            for (offset, column, coefficient) in terms:
                if offset > index:
                    break
                if column <= x:
                    total += coefficient * result[index - offset]
            result[index] = total % mod * inverses[index] % mod
    else:
        factor = (exponent + 1) % mod
        terms = [(offset, x, coefficient, factor * offset * coefficient % mod) for (offset, x, coefficient) in terms]
        for index in range(1, len(series)):
            x = index % width
            total = 0
            for (offset, column, coefficient, weighted) in terms:
                if offset > index:
                    break
                if column <= x:
                    total += (weighted - index * coefficient) % mod * result[index - offset]
            result[index] = total % mod * inverses[index] % mod
    return result

class MultivariateFormalPowerSeries:
    __slots__ = ('coefficients', 'base', 'mod')

    def __init__(self, coefficients=None, base=(), mod=DEFAULT_MOD):
        self.base = tuple(base)
        size = 1
        for radix in self.base:
            if radix <= 0:
                raise ValueError('radices must be positive')
            size *= radix
        if coefficients is None:
            coefficients = [0] * size
        if len(coefficients) != size:
            raise ValueError('coefficient length must equal product(base)')
        self.coefficients = [value % mod for value in coefficients]
        self.mod = mod
    f = property(lambda self: self.coefficients)

    def index(self, *indices):
        if len(indices) != len(self.base):
            raise IndexError('wrong number of multivariate indices')
        result = 0
        stride = 1
        for (value, radix) in zip(indices, self.base):
            if not 0 <= value < radix:
                raise IndexError('multivariate index out of range')
            result += value * stride
            stride *= radix
        return result
    id = index

    def get(self, *indices):
        return self.coefficients[self.index(*indices)]

    def set(self, *indices_and_value):
        (*indices, value) = indices_and_value
        self.coefficients[self.index(*indices)] = value % self.mod

    def _series(self, other):
        if not isinstance(other, MultivariateFormalPowerSeries):
            result = [0] * len(self.coefficients)
            result[0] = other % self.mod
            return result
        if self.base != other.base or self.mod != other.mod:
            raise ValueError('bases or moduli differ')
        return other.coefficients

    def __add__(self, other):
        source = self._series(other)
        return MultivariateFormalPowerSeries([(left + right) % self.mod for (left, right) in zip(self.coefficients, source)], self.base, self.mod)
    __radd__ = __add__

    def __neg__(self):
        return MultivariateFormalPowerSeries([-value % self.mod for value in self.coefficients], self.base, self.mod)

    def __sub__(self, other):
        return self + (-other if isinstance(other, MultivariateFormalPowerSeries) else -other)

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        if isinstance(other, MultivariateFormalPowerSeries):
            source = self._series(other)
            result = multivariate_multiplication(self.coefficients, source, self.base, self.mod)
        else:
            result = [value * other % self.mod for value in self.coefficients]
        return MultivariateFormalPowerSeries(result, self.base, self.mod)
    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, MultivariateFormalPowerSeries):
            return self * other.inverse()
        return self * pow(other, -1, self.mod)

    def derivative(self):
        return MultivariateFormalPowerSeries([index * value % self.mod for (index, value) in enumerate(self.coefficients)], self.base, self.mod)
    diff = derivative

    def integral(self):
        result = self.coefficients[:]
        inverses = _fps_multivariate_fps_inverses(len(result), self.mod)
        for index in range(1, len(result)):
            result[index] = result[index] * inverses[index] % self.mod
        return MultivariateFormalPowerSeries(result, self.base, self.mod)

    def inverse(self):
        if self.coefficients[0] == 0:
            raise ZeroDivisionError('constant coefficient is zero')
        result = _fps_multivariate_fps_sparse_2d(self.coefficients, self.base, self.mod, -1)
        if result is None:
            result = _fps_multivariate_fps_inverse_prefix(self.coefficients, self.base, self.mod, len(self.coefficients))
        return MultivariateFormalPowerSeries(result, self.base, self.mod)
    inv = inverse

    def logarithm(self):
        if self.coefficients[0] != 1:
            raise ValueError('constant coefficient must be one')
        size = len(self.coefficients)
        result = _fps_multivariate_fps_sparse_2d(self.coefficients, self.base, self.mod, logarithm=True)
        if result is None:
            result = _fps_multivariate_fps_log_prefix(self.coefficients, self.base, self.mod, size, _fps_multivariate_fps_inverses(size, self.mod))
        return MultivariateFormalPowerSeries(result, self.base, self.mod)
    log = logarithm

    def exponential(self):
        if self.coefficients[0] != 0:
            raise ValueError('constant coefficient must be zero')
        result = _fps_multivariate_fps_sparse_2d(self.coefficients, self.base, self.mod)
        if result is None:
            result = _fps_multivariate_fps_exp_prefix(self.coefficients, self.base, self.mod, len(self.coefficients))
        return MultivariateFormalPowerSeries(result, self.base, self.mod)
    exp = exponential

    def power(self, exponent):
        if exponent and self.coefficients[0]:
            values = _fps_multivariate_fps_sparse_2d(self.coefficients, self.base, self.mod, exponent)
            if values is not None:
                return MultivariateFormalPowerSeries(values, self.base, self.mod)
            if abs(exponent) > 8 and self.mod == DEFAULT_MOD and (len(self.coefficients) < self.mod):
                constant = self.coefficients[0]
                normalized = self * pow(constant, -1, self.mod)
                return (normalized.logarithm() * exponent).exponential() * pow(constant, exponent, self.mod)
        base = self
        if exponent < 0:
            base = self.inverse()
            exponent = -exponent
        result_values = [0] * len(self.coefficients)
        result_values[0] = 1
        result = MultivariateFormalPowerSeries(result_values, self.base, self.mod)
        while exponent:
            if exponent & 1:
                result = result * base
            exponent >>= 1
            if exponent:
                base = base * base
        return result
    pow = power
MultivariateFPS = MultivariateFormalPowerSeries
import sys

def main():
    read = sys.stdin.buffer.readline
    (n, m) = map(int, read().split())
    series = []
    for _ in range(n):
        series.extend(map(int, read().split()))
    result = MultivariateFormalPowerSeries(series, (m, n)).inverse().coefficients
    write = sys.stdout.write
    for i in range(0, n * m, m):
        write(' '.join(map(str, result[i:i + m])) + '\n')
if __name__ == '__main__':
    main()
