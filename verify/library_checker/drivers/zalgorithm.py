import sys

from library_codex.string.ZAlgorithm import z_algorithm

print(*z_algorithm(sys.stdin.buffer.readline().strip()))
