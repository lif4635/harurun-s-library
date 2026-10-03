import sys
from library_codex.number_theory.ModularArithmetic import modular_square_root

read = sys.stdin.buffer.readline
answers = [str(modular_square_root(*map(int, read().split()))) for _ in range(int(read()))]
sys.stdout.write("\n".join(answers) + "\n")
