import sys
from library_codex.number_theory.ModularRoot import primitive_root

read = sys.stdin.buffer.readline
answers = [str(primitive_root(int(read()))) for _ in range(int(read()))]
sys.stdout.write("\n".join(answers) + "\n")
