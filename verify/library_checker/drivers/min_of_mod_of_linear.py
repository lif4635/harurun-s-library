import sys

from library_codex.number_theory.MinMod import min_mod


read = sys.stdin.buffer.readline
result = [str(min_mod(*map(int, read().split()))) for _ in range(int(read()))]
sys.stdout.write("\n".join(result))
