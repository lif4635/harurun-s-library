import sys
from library_codex.number_theory.DiscreteLog import discrete_log

read = sys.stdin.buffer.readline
answers = [str(discrete_log(*map(int, read().split()))) for _ in range(int(read()))]
sys.stdout.write("\n".join(answers) + "\n")
