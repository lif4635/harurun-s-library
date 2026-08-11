"""個数penalty付き最適化から個数固定の最適値を復元する。"""


def _aliens_min(target, solve, max_abs_penalty):
    value_zero, count_zero = solve(0)
    if count_zero == target:
        return value_zero, 0
    lower = upper = 0
    value_lower = value_upper = value_zero
    count_lower = count_upper = count_zero
    if count_zero < target:
        lower = -1
        value_lower, count_lower = solve(lower)
        while count_lower < target:
            distance = upper - lower
            upper, value_upper, count_upper = lower, value_lower, count_lower
            lower -= distance * 2
            if lower < -max_abs_penalty:
                raise ValueError("target count was not bracketed by solve")
            value_lower, count_lower = solve(lower)
    else:
        upper = 1
        value_upper, count_upper = solve(upper)
        while count_upper > target:
            distance = upper - lower
            lower, value_lower, count_lower = upper, value_upper, count_upper
            upper += distance * 2
            if upper > max_abs_penalty:
                raise ValueError("target count was not bracketed by solve")
            value_upper, count_upper = solve(upper)
    if count_lower < target or count_upper > target:
        raise ValueError("solve counts must be nonincreasing in penalty")

    while lower + 1 < upper:
        middle = (lower + upper) // 2
        value, count = solve(middle)
        if count == target:
            return value - middle * target, middle
        if count > target:
            lower, value_lower, count_lower = middle, value, count
        else:
            upper, value_upper, count_upper = middle, value, count
    first = value_lower - lower * target
    second = value_upper - upper * target
    return (first, lower) if first >= second else (second, upper)


def aliens_trick(target, solve, minimize=True, max_abs_penalty=1 << 60):
    """solve(penalty)を使ってcount=targetのbase scoreとpenaltyを返す。"""
    if target < 0 or max_abs_penalty < 1:
        raise ValueError("target must be nonnegative and penalty limit positive")
    if minimize:
        return _aliens_min(target, solve, max_abs_penalty)

    def transformed(penalty):
        value, count = solve(-penalty)
        return -value, count

    value, penalty = _aliens_min(target, transformed, max_abs_penalty)
    return -value, -penalty
