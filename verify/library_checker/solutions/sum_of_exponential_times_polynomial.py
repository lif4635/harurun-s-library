"""0からlimitまでの整数を、同じ指数で累乗した値をまとめて求める。"""
from math import isqrt

def power_table(limit, exponent, mod=None):
    """result[i] = i**exponentとなる長さlimit+1の列を返す。mod指定時は剰余。"""
    if limit < 0 or exponent < 0:
        raise ValueError('limit and exponent must be nonnegative')
    if mod is None:
        return [value ** exponent for value in range(limit + 1)]
    if limit < 128 or exponent < 4 or mod <= 0:
        return [pow(value, exponent, mod) for value in range(limit + 1)]
    values = [0] * (limit + 1)
    for prime in range(2, isqrt(limit) + 1):
        if values[prime] == 0:
            for multiple in range(prime * prime, limit + 1, prime):
                values[multiple] = prime
    values[0] = pow(0, exponent, mod)
    values[1] = 1 % mod
    for value in range(2, limit + 1):
        divisor = values[value]
        if divisor:
            values[value] = values[divisor] * values[value // divisor] % mod
        else:
            values[value] = pow(value, exponent, mod)
    return values
'多項式と指数関数の積の有限和・極限和を計算する。'
DEFAULT_MOD = 998244353

def _polynomial_polynomial_exponential_sum_inverse_factorials(size, mod):
    factorial = 1
    for value in range(2, size + 1):
        factorial = factorial * value % mod
    inverse = pow(factorial, -1, mod)
    result = [1] * (size + 1)
    result[size] = inverse
    for value in range(size, 1, -1):
        inverse = inverse * value % mod
        result[value - 1] = inverse
    return (factorial, result)

def _polynomial_polynomial_exponential_sum_interpolate(values, point, mod, inverse_factorials):
    point %= mod
    size = len(values)
    if point < size:
        return values[point] % mod
    left = [1] * size
    product = 1
    for index in range(size - 1):
        product = product * (point - index) % mod
        left[index + 1] = product
    right = 1
    result = 0
    sign = 1
    for index in range(size - 1, -1, -1):
        term = values[index] * left[index] % mod * right % mod
        term = term * inverse_factorials[index] % mod * inverse_factorials[size - 1 - index] % mod
        result += sign * term
        right = right * (point - index) % mod
        sign = -sign
    return result % mod

def _polynomial_polynomial_exponential_sum_limit(values, ratio, mod, factorial, inverse_factorials):
    degree = len(values) - 1
    inverse_ratio = pow(ratio, -1, mod)
    coefficient = 0
    answer = 0
    sign = 1
    for index in range(degree, -1, -1):
        term = inverse_factorials[degree - index] * inverse_factorials[index + 1] % mod
        coefficient = (coefficient * inverse_ratio + sign * term) % mod
        answer = (answer + coefficient * values[index]) % mod
        sign = -sign
    return answer * factorial % mod * pow(ratio, degree, mod) % mod * pow(pow(1 - ratio, degree + 1, mod), -1, mod) % mod

def limit_sum_polynomial_exponential(values, ratio, mod=DEFAULT_MOD):
    """f(0), ..., f(d)から、母関数の無限和をratioで評価した余りを返す。"""
    if not values:
        raise ValueError('at least one sample is required')
    ratio %= mod
    if ratio == 1:
        raise ValueError('the infinite formal sum requires ratio != 1')
    if ratio == 0:
        return values[0] % mod
    (factorial, inverse_factorials) = _polynomial_polynomial_exponential_sum_inverse_factorials(len(values), mod)
    return _polynomial_polynomial_exponential_sum_limit(values, ratio, mod, factorial, inverse_factorials)

def sum_polynomial_exponential(values, ratio, count, mod=DEFAULT_MOD):
    """f(0), ..., f(d)から、count項の等比重み付き和を法で割った余りを返す。"""
    if not values:
        raise ValueError('at least one sample is required')
    if count <= 0:
        return 0
    ratio %= mod
    if ratio == 0:
        return values[0] % mod
    size = len(values)
    if count <= size:
        power = 1
        answer = 0
        for index in range(count):
            answer = (answer + power * values[index]) % mod
            power = power * ratio % mod
        return answer
    (factorial, inverse_factorials) = _polynomial_polynomial_exponential_sum_inverse_factorials(size, mod)
    if ratio == 1:
        prefixes = [0] * (size + 1)
        total = 0
        for index in range(size):
            total = (total + values[index]) % mod
            prefixes[index + 1] = total
        return _polynomial_polynomial_exponential_sum_interpolate(prefixes, count, mod, inverse_factorials)
    constant = _polynomial_polynomial_exponential_sum_limit(values, ratio, mod, factorial, inverse_factorials)
    inverse_ratio = pow(ratio, -1, mod)
    inverse_power = 1
    power = 1
    prefix = 0
    adjusted = [0] * size
    for index in range(size):
        prefix = (prefix + power * values[index]) % mod
        adjusted[index] = (prefix - constant) * inverse_power % mod
        power = power * ratio % mod
        inverse_power = inverse_power * inverse_ratio % mod
    last = count - 1
    return (pow(ratio, last, mod) * _polynomial_polynomial_exponential_sum_interpolate(adjusted, last, mod, inverse_factorials) + constant) % mod
import sys
(ratio, degree, count) = map(int, sys.stdin.buffer.read().split())
values = power_table(degree, degree, 998244353)
print(sum_polynomial_exponential(values, ratio, count))
