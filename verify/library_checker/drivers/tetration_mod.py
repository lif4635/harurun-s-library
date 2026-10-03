import sys
from library_codex.number_theory.TetrationMod import tetration_mod

read = sys.stdin.buffer.readline
answers = [str(tetration_mod(*map(int, read().split()))) for _ in range(int(read()))]
sys.stdout.write("\n".join(answers) + "\n")
