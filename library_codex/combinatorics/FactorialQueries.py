"""998244353を法とする、離れた添字の階乗をまとめて求める。"""

from library_codex.convolution.NTT998 import multiply

_BLOCK_SIZE = 1024


def _extend_samples(values, count, inverse):
    size = len(values)
    if count <= size:
        return values[:count]
    factorial = 1
    for i in range(2, size):
        factorial = factorial * i % 998244353
    inverse_factorial = [1] * size
    inverse_factorial[-1] = pow(factorial, -1, 998244353)
    for i in range(size - 1, 0, -1):
        inverse_factorial[i - 1] = inverse_factorial[i] * i % 998244353
    weighted = [0] * size
    for i in range(size):
        value = values[i] * inverse_factorial[i] % 998244353
        value = value * inverse_factorial[size - 1 - i] % 998244353
        weighted[i] = -value % 998244353 if (size - 1 - i) & 1 else value
    product = multiply(weighted, inverse[1:count])
    result = values[:]
    falling = factorial * size % 998244353
    for x in range(size, count):
        result.append(falling * product[x - 1] % 998244353)
        falling = falling * (x + 1) % 998244353 * inverse[x - size + 1] % 998244353
    return result


def _restore_complements(result, indices):
    prefix = []
    value = 1
    for i, n in enumerate(indices):
        if 499122176 < n < 998244353:
            prefix.append((i, value))
            value = value * result[i] % 998244353
    value = pow(value, -1, 998244353)
    for i, before in reversed(prefix):
        inverse = value * before % 998244353
        value = value * result[i] % 998244353
        result[i] = inverse if indices[i] & 1 else -inverse % 998244353
    return result


def factorials(indices):
    """各indices[i]!を998244353で割った余りを、入力順のlistで返す。"""
    indices = list(indices)
    if any(n < 0 for n in indices):
        raise ValueError("factorial indices must be nonnegative")
    result = [0] * len(indices)
    queries = sorted((min(n, 998244352 - n), i)
                     for i, n in enumerate(indices) if n < 998244353)
    if not queries:
        return result
    maximum = queries[-1][0]
    if maximum <= 262144:
        value = 1
        previous = 0
        for n, i in queries:
            for x in range(previous + 1, n + 1):
                value = value * x % 998244353
            result[i] = value
            previous = n
        return _restore_complements(result, indices)
    block = _BLOCK_SIZE
    count = maximum // block
    limit = max(block * 2, count)
    inverse = [0, 1] + [0] * (limit - 1)
    for i in range(2, limit + 1):
        inverse[i] = -(998244353 // i) * inverse[998244353 % i] % 998244353
    samples = [1]
    width = 1
    while width < block:
        extended = _extend_samples(samples, width * 4, inverse)
        samples = [extended[i * 2] * extended[i * 2 + 1] % 998244353
                   * ((i * 2 + 1) * width) % 998244353 for i in range(width * 2)]
        width *= 2
    samples = _extend_samples(samples, count, inverse)
    blocks = [1] * (count + 1)
    for i in range(count):
        blocks[i + 1] = blocks[i] * samples[i] % 998244353 * ((i + 1) * block) % 998244353
    previous = -1
    value = 1
    for n, i in queries:
        start = n // block * block
        if previous < start:
            previous = start
            value = blocks[n // block]
        for x in range(previous + 1, n + 1):
            value = value * x % 998244353
        result[i] = value
        previous = n
    return _restore_complements(result, indices)
