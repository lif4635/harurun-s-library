import sys

def sum_totient_fast(limit, mod=None):
    if limit < 1:
        return 0
    quotients = set()
    left = 1
    while left <= limit:
        quotient = limit // left
        quotients.add(quotient)
        left = limit // quotient + 1
    prefix = {}
    for value in sorted(quotients):
        result = value * (value + 1) // 2
        lower = 2
        while lower <= value:
            quotient = value // lower
            upper = value // quotient + 1
            result -= (upper - lower) * prefix[quotient]
            lower = upper
        prefix[value] = result if mod is None else result % mod
    return prefix[limit]

print(sum_totient_fast(int(sys.stdin.buffer.read()), 998244353))
