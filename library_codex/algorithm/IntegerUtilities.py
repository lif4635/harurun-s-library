"""非負整数の整数n乗根。"""


def integer_nth_root(number, degree):
    """非負整数numberのdegree乗根をNewton法で切り捨てて返す。"""
    if number < 0:
        raise ValueError("number must be nonnegative")
    if degree <= 0:
        raise ValueError("degree must be positive")
    if number < 2 or degree == 1:
        return number
    bits = number.bit_length()
    if degree >= bits:
        return 1
    root = 1 << ((bits + degree - 1) // degree)
    exponent = degree - 1
    while True:
        next_root = (exponent * root + number // root ** exponent) // degree
        if next_root >= root:
            break
        root = next_root

    # Integer Newton iteration may stop one step next to floor(root).
    while (root + 1) ** degree <= number:
        root += 1
    while root ** degree > number:
        root -= 1
    return root
