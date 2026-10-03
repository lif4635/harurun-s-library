import sys

from library_codex.fps998.FPS import fps_product

read = sys.stdin.buffer.readline
polynomials = [list(map(int, read().split()))[1:] for _ in range(int(read()))]
print(*fps_product(polynomials))
