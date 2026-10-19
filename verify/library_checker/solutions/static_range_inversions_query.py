"""複数の半開区間をまとめて受け取り、それぞれの転倒数を求める。"""
from math import isqrt

def range_inversions(values, queries):
    """queriesの各[left, right)内の転倒数を、問い合わせ順のlistで返す。"""
    values = list(values)
    queries = list(queries)
    n = len(values)
    q = len(queries)
    for (left, right) in queries:
        if not 0 <= left <= right <= n:
            raise IndexError('invalid half-open range')
    if not q:
        return []
    mapping = {value: i + 1 for (i, value) in enumerate(sorted(set(values)))}
    ranks = [mapping[value] for value in values]
    m = len(mapping)
    bit = [0] * (m + 1)
    width = max(1, n // max(1, isqrt(q)))
    order = sorted(range(q), key=lambda i: (queries[i][0] // width, -queries[i][1] if queries[i][0] // width & 1 else queries[i][1]))
    answers = [0] * q
    left = right = inv = 0
    for index in order:
        (l, r) = queries[index]
        while left > l:
            left -= 1
            value = ranks[left]
            j = value - 1
            while j:
                inv += bit[j]
                j &= j - 1
            j = value
            while j <= m:
                bit[j] += 1
                j += j & -j
        while right < r:
            value = ranks[right]
            inv += right - left
            j = value
            while j:
                inv -= bit[j]
                j &= j - 1
            j = value
            while j <= m:
                bit[j] += 1
                j += j & -j
            right += 1
        while left < l:
            value = ranks[left]
            j = value - 1
            while j:
                inv -= bit[j]
                j &= j - 1
            j = value
            while j <= m:
                bit[j] -= 1
                j += j & -j
            left += 1
        while right > r:
            right -= 1
            value = ranks[right]
            j = value
            while j <= m:
                bit[j] -= 1
                j += j & -j
            inv -= right - left
            j = value
            while j:
                inv += bit[j]
                j &= j - 1
        answers[index] = inv
    return answers
import sys

def main():
    read = sys.stdin.buffer.readline
    (n, q) = map(int, read().split())
    values = list(map(int, read().split()))
    queries = [tuple(map(int, read().split())) for _ in range(q)]
    sys.stdout.write('\n'.join(map(str, range_inversions(values, queries))))
if __name__ == '__main__':
    main()
