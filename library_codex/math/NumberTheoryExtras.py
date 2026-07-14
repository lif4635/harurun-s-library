from math import gcd, isqrt

from library_codex.math.ModularArithmetic import modular_square_root
from library_codex.prime.Factorization import factor_count, euler_phi


def floor_div(numerator, denominator):
    if denominator == 0:
        raise ZeroDivisionError("integer division by zero")
    return numerator // denominator


def ceil_div(numerator, denominator):
    if denominator == 0:
        raise ZeroDivisionError("integer division by zero")
    return -((-numerator) // denominator)


def strict_floor_div(numerator, denominator):
    """Largest integer strictly smaller than numerator / denominator."""
    quotient, remainder = divmod(numerator, denominator)
    return quotient - (remainder == 0)


def strict_ceil_div(numerator, denominator):
    """Smallest integer strictly larger than numerator / denominator."""
    quotient = ceil_div(numerator, denominator)
    return quotient + (numerator % denominator == 0)


def quadratic_equation_mod(a, b, c, prime):
    """All roots of a*x^2+b*x+c over an odd prime field."""
    if prime == 2:
        return [value for value in range(2)
                if (a * value * value + b * value + c) % 2 == 0]
    a %= prime
    b %= prime
    c %= prime
    if a == 0:
        if b == 0:
            if c == 0:
                raise ValueError("the zero polynomial has every element as a root")
            return []
        return [(-c * pow(b, -1, prime)) % prime]
    discriminant = (b * b - 4 * a * c) % prime
    root = modular_square_root(discriminant, prime)
    if root == -1:
        return []
    inverse = pow(2 * a % prime, -1, prime)
    first = (-b + root) * inverse % prime
    second = (-b - root) * inverse % prime
    return [first] if first == second else sorted((first, second))


def _pow_mod_with_bound(base, exponent, modulus):
    """Return base**exponent mod modulus and whether the exact value is < modulus."""
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    modular_result = 1 % modulus
    modular_base = base % modulus
    capped_result = 1
    capped_base = min(base, modulus)
    power = exponent
    while power:
        if power & 1:
            modular_result = modular_result * modular_base % modulus
            capped_result = min(modulus, capped_result * capped_base)
        power >>= 1
        if power:
            modular_base = modular_base * modular_base % modulus
            capped_base = min(modulus, capped_base * capped_base)
    return modular_result, capped_result < modulus


def tetration_mod(base, height, modulus):
    """base ↑↑ height modulo modulus; 0 ↑↑ height follows 0**0 == 1."""
    if base < 0 or height < 0 or modulus <= 0:
        raise ValueError("base/height must be nonnegative and modulus positive")
    if base == 0:
        value = 1 if height & 1 == 0 else 0
        return value % modulus
    if base == 1:
        return 1 % modulus
    frames = []
    current_height = height
    current_modulus = modulus
    while True:
        if current_modulus == 1:
            value, below = 0, False
            break
        if current_height == 0:
            value, below = 1 % current_modulus, 1 < current_modulus
            break
        if current_height == 1:
            value, below = base % current_modulus, base < current_modulus
            break
        next_modulus = euler_phi(current_modulus)
        frames.append((current_modulus, next_modulus))
        current_modulus = next_modulus
        current_height -= 1
    while frames:
        parent_modulus, exponent_modulus = frames.pop()
        exponent = value if below else value + exponent_modulus
        value, power_below = _pow_mod_with_bound(base, exponent, parent_modulus)
        below = below and power_below
    return value % modulus


class FastPower:
    """Fixed-base powers with O(number of exponent blocks) queries."""

    __slots__ = ("mod", "block_bits", "mask", "tables", "identity")

    def __init__(self, base, mod, max_exponent=(1 << 63) - 1, block_bits=10):
        if mod <= 0 or max_exponent < 0 or block_bits <= 0:
            raise ValueError("invalid fixed-power parameters")
        self.mod = mod
        self.block_bits = block_bits
        width = 1 << block_bits
        self.mask = width - 1
        self.identity = 1 % mod
        blocks = max(1, (max_exponent.bit_length() + block_bits - 1) // block_bits)
        tables = []
        current_base = base % mod
        for _ in range(blocks):
            table = [self.identity] * width
            for index in range(1, width):
                table[index] = table[index - 1] * current_base % mod
            tables.append(table)
            current_base = table[-1] * current_base % mod
        self.tables = tables

    def __call__(self, exponent):
        if exponent < 0 or exponent.bit_length() > len(self.tables) * self.block_bits:
            raise ValueError("exponent is outside the precomputed range")
        result = self.identity
        shift = 0
        while exponent:
            result = result * self.tables[shift][exponent & self.mask] % self.mod
            exponent >>= self.block_bits
            shift += 1
        return result


class GaussianInteger:
    __slots__ = ("real", "imag")

    def __init__(self, real=0, imag=0):
        self.real = real
        self.imag = imag

    @property
    def x(self):
        return self.real

    @property
    def y(self):
        return self.imag

    def norm(self):
        return self.real * self.real + self.imag * self.imag

    def conjugate(self):
        return GaussianInteger(self.real, -self.imag)

    conj = conjugate

    def __add__(self, other):
        return GaussianInteger(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other):
        return GaussianInteger(self.real - other.real, self.imag - other.imag)

    def __neg__(self):
        return GaussianInteger(-self.real, -self.imag)

    def __mul__(self, other):
        if isinstance(other, int):
            return GaussianInteger(self.real * other, self.imag * other)
        return GaussianInteger(
            self.real * other.real - self.imag * other.imag,
            self.real * other.imag + self.imag * other.real,
        )

    def __eq__(self, other):
        return (isinstance(other, GaussianInteger)
                and self.real == other.real and self.imag == other.imag)

    def __repr__(self):
        return f"GaussianInteger({self.real}, {self.imag})"

    def __pow__(self, exponent):
        if exponent < 0:
            raise ValueError("negative Gaussian powers are not integral")
        result = GaussianInteger(1)
        base = self
        while exponent:
            if exponent & 1:
                result = result * base
            exponent >>= 1
            if exponent:
                base = base * base
        return result

    def __divmod__(self, other):
        norm = other.norm()
        if norm == 0:
            raise ZeroDivisionError("Gaussian integer division by zero")
        product = self * other.conjugate()

        def nearest(value):
            quotient, remainder = divmod(value, norm)
            if remainder * 2 >= norm:
                quotient += 1
            return quotient

        quotient = GaussianInteger(nearest(product.real), nearest(product.imag))
        return quotient, self - quotient * other

    def __floordiv__(self, other):
        return divmod(self, other)[0]

    def __mod__(self, other):
        return divmod(self, other)[1]


def gaussian_gcd(first, second):
    while second != GaussianInteger():
        first, second = second, first % second
    return first


def _prime_two_squares(prime):
    if prime == 2:
        return GaussianInteger(1, 1)
    if prime & 3 == 3:
        return None
    root = modular_square_root(-1, prime)
    if root == -1:
        return None
    previous, current = prime, root
    while current * current > prime:
        previous, current = current, previous % current
    remaining = prime - current * current
    imaginary = isqrt(remaining)
    if imaginary * imaginary != remaining:
        root = prime - root
        previous, current = prime, root
        while current * current > prime:
            previous, current = current, previous % current
        remaining = prime - current * current
        imaginary = isqrt(remaining)
    if imaginary * imaginary != remaining:
        raise ArithmeticError("Cornacchia failed")
    return GaussianInteger(current, imaginary)


def two_square_representations(number):
    """All ordered nonnegative (x,y) with x*x+y*y == number."""
    if number < 0:
        return []
    if number == 0:
        return [(0, 0)]
    current = [GaussianInteger(1)]
    for prime, exponent in factor_count(number).items():
        if prime & 3 == 3:
            if exponent & 1:
                return []
            choices = [GaussianInteger(prime ** (exponent >> 1))]
        elif prime == 2:
            choices = [GaussianInteger(1, 1) ** exponent]
        else:
            base = _prime_two_squares(prime)
            powers = [GaussianInteger(1)] * (exponent + 1)
            conjugate_powers = [GaussianInteger(1)] * (exponent + 1)
            conjugate = base.conjugate()
            for index in range(exponent):
                powers[index + 1] = powers[index] * base
                conjugate_powers[index + 1] = conjugate_powers[index] * conjugate
            choices = [powers[index] * conjugate_powers[exponent - index]
                       for index in range(exponent + 1)]
        next_values = []
        for first in current:
            for second in choices:
                next_values.append(first * second)
        current = next_values
    result = set()
    for value in current:
        real = abs(value.real)
        imaginary = abs(value.imag)
        result.add((real, imaginary))
        result.add((imaginary, real))
    return sorted(result)


class RationalNumberSearch:
    """Adaptive Stern--Brocot search with numerator/denominator bounds."""

    __slots__ = ("maximum", "a0", "b0", "a1", "b1", "left", "right", "state")

    def __init__(self, maximum):
        if maximum <= 0:
            raise ValueError("maximum must be positive")
        self.maximum = maximum
        self.a0, self.b0 = 0, 1
        self.a1, self.b1 = 1, 0
        self.left = self.right = 0
        self.state = 0

    def has_next(self):
        return self.state >= 0

    def get_next(self):
        state = self.state
        if state == 0:
            return self.a0 + self.a1, self.b0 + self.b1
        middle = (self.left + self.right) >> 1
        if state == 1:
            return self.a0 + self.right * self.a1, self.b0 + self.right * self.b1
        if state == 2:
            return self.a1 + self.right * self.a0, self.b1 + self.right * self.b0
        if state == 3:
            return self.a0 + middle * self.a1, self.b0 + middle * self.b1
        if state == 4:
            return self.a1 + middle * self.a0, self.b1 + middle * self.b0
        raise StopIteration

    def give(self, to_right):
        direction = 1 if to_right else 0
        state = self.state
        if state == 0:
            self.left, self.right = 1, 2
            if self.a0 + self.a1 > self.maximum or self.b0 + self.b1 > self.maximum:
                self.state = -1
            else:
                self.state = 1 if to_right else 2
        elif state in (1, 2):
            if direction ^ (2 - state):
                self.state += 2
            else:
                self.left <<= 1
                self.right <<= 1
        elif state in (3, 4):
            if direction ^ (4 - state):
                self.right = (self.left + self.right) >> 1
            else:
                self.left = (self.left + self.right) >> 1
        while self._normalize():
            pass

    def _normalize(self):
        state = self.state
        if state < 0:
            return False
        if state == 0:
            if self.a0 + self.a1 > self.maximum or self.b0 + self.b1 > self.maximum:
                self.state = -1
            return False
        if state in (1, 2):
            changed = False
            if state == 1:
                pairs = ((self.a0, self.a1), (self.b0, self.b1))
            else:
                pairs = ((self.a1, self.a0), (self.b1, self.b0))
            for base, step in pairs:
                if base + self.right * step > self.maximum:
                    self.right = (self.maximum - base) // step + 1
                    changed = True
            if changed:
                self.state += 2
                return True
            return False
        if self.left + 1 != self.right:
            return False
        if state == 3:
            self.a0 += self.a1 * self.left
            self.b0 += self.b1 * self.left
            self.a1 += self.a0
            self.b1 += self.b0
        else:
            self.a1 += self.a0 * self.left
            self.b1 += self.b0 * self.left
            self.a0 += self.a1
            self.b0 += self.b1
        self.state = 0
        return True


FastPow = FastPower
QuadraticEquation = quadratic_equation_mod
RepresentTwoSquare = two_square_representations
two_square = two_square_representations
tetration = tetration_mod
