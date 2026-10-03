import sys

from library_codex.fps998.FPS import fps_log

read = sys.stdin.buffer.readline
n = int(read())
print(*fps_log(list(map(int, read().split())), n))
