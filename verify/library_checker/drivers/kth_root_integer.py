import sys
from library_codex.number_theory.ModularRoot import floor_kth_root

read = sys.stdin.buffer.readline
answers = [str(floor_kth_root(*map(int, read().split()))) for _ in range(int(read()))]
sys.stdout.write("\n".join(answers) + "\n")
