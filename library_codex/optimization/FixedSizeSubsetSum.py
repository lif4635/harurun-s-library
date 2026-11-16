"""異なる整数をちょうどk個選んで作れる和を、重複なく昇順に列挙する。"""

from itertools import combinations
from math import gcd


def fixed_size_subset_sums(values, k):
    """入力を集合として扱い、異なるk個の値の和を昇順listで返す。"""
    if k < 0:
        raise ValueError("k must be nonnegative")
    values = sorted(set(values))
    n = len(values)
    if k > n:
        return []
    total = sum(values)
    complement = k > n - k
    if complement:
        k = n - k
    if k == 0:
        return [total if complement else 0]
    if k == 1:
        return [total - value for value in reversed(values)] if complement else values
    ways = 1
    for i in range(1, k + 1):
        ways = ways * (n - i + 1) // i
        if ways > 32768:
            break
    if ways <= 32768:
        result = sorted({sum(chosen) for chosen in combinations(values, k)})
    else:
        base = values[0]
        step = 0
        for value in values:
            step = gcd(step, value - base)
        normalized = [(value - base) // step for value in values]
        low, high = sum(normalized[:k]), sum(normalized[-k:])
        if normalized[-1] == n - 1:
            result = [k * base + step * value for value in range(low, high + 1)]
        else:
            dp = [1] + [0] * k
            for index, value in enumerate(normalized):
                for count in range(min(k, index + 1), 0, -1):
                    dp[count] |= dp[count - 1] << value
            packed = (dp[k] >> low).to_bytes((high - low + 8) // 8, "little")
            result = []
            for index, byte in enumerate(packed):
                while byte:
                    bit = byte & -byte
                    result.append(k * base + step * (low + 8 * index + bit.bit_length() - 1))
                    byte ^= bit
    return [total - value for value in reversed(result)] if complement else result
