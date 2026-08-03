"""nを整数で割った商が等しい添字区間を列挙する。"""

def enumerate_quotient(number):
    """Yield ``(number//x, left, right)`` for maximal x ranges [left,right)."""
    if number < 0:
        raise ValueError("number must be nonnegative")
    left = 1
    while left <= number:
        quotient = number // left
        right = number // quotient + 1
        yield quotient, left, right
        left = right

