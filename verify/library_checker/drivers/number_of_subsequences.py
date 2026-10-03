import sys

from library_codex.string.Subsequence import count_distinct_subsequences

read = sys.stdin.buffer.readline
n = int(read())
print(count_distinct_subsequences(map(int, read().split()), 998244353))
