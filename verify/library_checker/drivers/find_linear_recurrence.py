import sys
from library_codex.fps998.LinearRecurrence import berlekamp_massey

read = sys.stdin.buffer.readline
n = int(read())
coefficients = berlekamp_massey(list(map(int, read().split())))
print(len(coefficients))
print(*coefficients)
