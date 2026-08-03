"""符号を含む整数除算の床・天井と厳密不等号版を計算する。"""

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

