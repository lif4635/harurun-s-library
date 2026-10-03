import sys

from library_codex.fps998.FPS import fps_sqrt

read = sys.stdin.buffer.readline
n = int(read())
answer = fps_sqrt(list(map(int, read().split())), n)
if answer is None:
    print(-1)
else:
    print(*answer)
