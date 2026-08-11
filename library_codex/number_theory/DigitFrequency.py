"""整数区間を位取り表記したときの各digit出現数を数える。"""


def _count_below(upper, base):
    result = [0] * base
    if upper <= 0:
        return result
    result[0] = 1
    maximum = upper - 1
    factor = 1
    while factor <= maximum:
        higher = maximum // (factor * base)
        current = maximum // factor % base
        lower = maximum % factor
        for digit in range(1, base):
            result[digit] += higher * factor
            if current > digit:
                result[digit] += factor
            elif current == digit:
                result[digit] += lower + 1
        if higher:
            result[0] += (higher - 1) * factor
            if current:
                result[0] += factor
            else:
                result[0] += lower + 1
        factor *= base
    return result


def digit_frequency(lower, upper, base=10):
    """半開整数区間[lower, upper)の標準表記に現れるdigit数を返す。"""
    if not 0 <= lower <= upper:
        raise ValueError("0 <= lower <= upper is required")
    if base < 2:
        raise ValueError("base must be at least 2")
    high = _count_below(upper, base)
    low = _count_below(lower, base)
    return [first - second for first, second in zip(high, low)]
