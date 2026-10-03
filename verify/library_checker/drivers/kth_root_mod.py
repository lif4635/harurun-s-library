import sys
from library_codex.number_theory.ModularRoot import modular_kth_root

read = sys.stdin.buffer.readline
answers = []
for _ in range(int(read())):
    exponent, value, prime = map(int, read().split())
    answers.append(str(modular_kth_root(value, exponent, prime)))
sys.stdout.write("\n".join(answers) + "\n")
