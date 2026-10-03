import sys
from library_codex.prime.Factorization import is_prime

read = sys.stdin.buffer.readline
answers = ["Yes" if is_prime(int(read())) else "No" for _ in range(int(read()))]
sys.stdout.write("\n".join(answers) + "\n")
