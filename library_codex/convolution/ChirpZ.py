"""等比数列上の多項式評価をchirp-z変換でまとめて求める。"""

from library_codex.convolution.NTT import convolution, get_ntt, primitive_root

DEFAULT_MOD = 998244353

def chirp_z(polynomial, ratio, count=None, start=1, mod=DEFAULT_MOD):
    """Return f(start*ratio^i) for i=0..count-1 by Bluestein."""
    polynomial = [value % mod for value in polynomial]
    if count is None:
        count = len(polynomial)
    if count < 0:
        raise ValueError("count must be nonnegative")
    if not polynomial or count == 0:
        return [0] * count
    if start % mod != 1:
        power = 1
        for i in range(len(polynomial)):
            polynomial[i] = polynomial[i] * power % mod
            power = power * start % mod
    ratio %= mod
    if ratio == 0:
        result = [polynomial[0]] * count
        result[0] = sum(polynomial) % mod
        return result
    length = len(polynomial)
    triangular = [1] * (count + length)
    inverse_triangular = [1] * max(count, length)
    step = 1
    for i in range(1, len(triangular)):
        triangular[i] = triangular[i - 1] * step % mod
        step = step * ratio % mod
    inverse_ratio = pow(ratio, -1, mod)
    step = 1
    for i in range(1, len(inverse_triangular)):
        inverse_triangular[i] = inverse_triangular[i - 1] * step % mod
        step = step * inverse_ratio % mod
    for i in range(length):
        polynomial[i] = polynomial[i] * inverse_triangular[i] % mod
    polynomial.reverse()
    product = convolution(polynomial, triangular, mod)
    return [product[length - 1 + i] * inverse_triangular[i] % mod
            for i in range(count)]

