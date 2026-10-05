import sys

from library_codex.rational.FractionSearch import rational_bounds


read = sys.stdin.buffer.readline
result = []
for _ in range(int(read())):
    limit, numerator, denominator = map(int, read().split())
    lower, upper = rational_bounds(numerator, denominator, limit)
    result.append("%d %d %d %d" % (lower + upper))
sys.stdout.write("\n".join(result))
