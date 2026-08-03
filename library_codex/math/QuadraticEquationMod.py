"""法の下で二次方程式の解を列挙する。"""

from library_codex.math.ModularArithmetic import modular_square_root

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

