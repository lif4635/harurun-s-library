"""係数の積の代わりにmin、総和の代わりにmaxを使う畳み込みと、その逆を求める。"""


def _extreme_conv(a, b, reverse):
    n, m = len(a), len(b)
    if not n or not m:
        return []
    order = [(value, index, 0) for index, value in enumerate(a)]
    order.extend((value, index, 1) for index, value in enumerate(b))
    order.sort(reverse=reverse)
    remaining = (1 << (n + m - 1)) - 1
    active_a = active_b = 0
    result = [None] * (n + m - 1)
    for value, index, side in order:
        if side:
            fresh = (active_a << index) & remaining
            active_b |= 1 << index
        else:
            fresh = (active_b << index) & remaining
            active_a |= 1 << index
        remaining ^= fresh
        while fresh:
            bit = fresh & -fresh
            result[bit.bit_length() - 1] = value
            fresh ^= bit
        if not remaining:
            break
    return result


def max_min_conv(a, b):
    """result[k] = max(min(a[i], b[j]) for i+j=k)を返す。"""
    return _extreme_conv(a, b, True)


def min_max_conv(a, b):
    """result[k] = min(max(a[i], b[j]) for i+j=k)を返す。"""
    return _extreme_conv(a, b, False)
