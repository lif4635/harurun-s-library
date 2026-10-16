from math import isqrt
import sys


def prime_count(number):
    """Lucy-DP prime counting in about O(n^(3/4)/log n)."""
    if number < 2:
        return 0
    quotients = []
    left = 1
    while left <= number:
        quotient = number // left
        quotients.append(quotient)
        left = number // quotient + 1
    index = {value: i for i, value in enumerate(quotients)}
    count = [value - 1 for value in quotients]
    limit = isqrt(number)
    composite = bytearray(limit + 1)
    for prime in range(2, limit + 1):
        if composite[prime]:
            continue
        previous = count[index[prime - 1]]
        square = prime * prime
        for i, value in enumerate(quotients):
            if value < square:
                break
            count[i] -= count[index[value // prime]] - previous
        start = square
        for multiple in range(start, limit + 1, prime):
            composite[multiple] = 1
    return count[0]


print(prime_count(int(sys.stdin.buffer.read())))
