"""固定した底の累乗値をまとめて前計算する。"""

def power_table(limit, exponent, mod=None):
    if limit < 0 or exponent < 0:
        raise ValueError("limit and exponent must be nonnegative")
    if mod is None:
        return [value ** exponent for value in range(limit + 1)]
    return [pow(value, exponent, mod) for value in range(limit + 1)]

