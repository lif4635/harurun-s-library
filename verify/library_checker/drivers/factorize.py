import sys
from library_codex.prime.Factorization import prime_factors

read = sys.stdin.buffer.readline
answers = []
for _ in range(int(read())):
    factors = prime_factors(int(read()))
    answers.append(" ".join(map(str, [len(factors)] + factors)))
sys.stdout.write("\n".join(answers) + "\n")
