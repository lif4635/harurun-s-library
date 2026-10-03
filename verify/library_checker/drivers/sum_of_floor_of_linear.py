import sys
from library_codex.number_theory.FloorSum import floor_sum

read = sys.stdin.buffer.readline
answers = [str(floor_sum(*map(int, read().split()))) for _ in range(int(read()))]
sys.stdout.write("\n".join(answers) + "\n")
