import sys

from library_codex.fps998.FPS import taylor_shift

read = sys.stdin.buffer.readline
n, shift = map(int, read().split())
print(*taylor_shift(list(map(int, read().split())), shift))
