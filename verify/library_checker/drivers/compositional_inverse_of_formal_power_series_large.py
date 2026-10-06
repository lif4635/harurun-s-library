import sys

from library_codex.fps998.Composition import fps_compositional_inv


read = sys.stdin.buffer.readline
size = int(read())
values = list(map(int, read().split()))
print(*fps_compositional_inv(values, size))
