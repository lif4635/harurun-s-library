import sys

from library_codex.fps998.FPS import fps_pow

read = sys.stdin.buffer.readline
n, exponent = map(int, read().split())
print(*fps_pow(list(map(int, read().split())), exponent, n))
