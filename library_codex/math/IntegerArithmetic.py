"""整数のgcd・lcm・拡張gcdと法逆元を計算する。"""

DEFAULT_MOD = 998244353

def gcd(first, second):
    first = abs(first)
    second = abs(second)
    while second:
        first, second = second, first % second
    return first

def lcm(first, second):
    return 0 if not first or not second else abs(first // gcd(first, second) * second)

def extended_gcd(first, second):
    """Return (g,x,y) with first*x + second*y = g = gcd(first,second)."""
    old_r, r = first, second
    old_x, x = 1, 0
    old_y, y = 0, 1
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_x, x = x, old_x - quotient * x
        old_y, y = y, old_y - quotient * y
    if old_r < 0:
        old_r, old_x, old_y = -old_r, -old_x, -old_y
    return old_r, old_x, old_y

def inverse_mod(value, modulus):
    gcd, inverse, _ = extended_gcd(value, modulus)
    if gcd != 1:
        raise ValueError("inverse does not exist")
    return inverse % modulus

def inverse_table(size, mod=DEFAULT_MOD):
    if size >= mod:
        raise ValueError("table entries must be invertible")
    inverse = [0] * (size + 1)
    if size:
        inverse[1] = 1
    for value in range(2, size + 1):
        inverse[value] = mod - mod // value * inverse[mod % value] % mod
    return inverse

