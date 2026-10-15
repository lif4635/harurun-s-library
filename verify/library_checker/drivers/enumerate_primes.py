import sys
from library_codex.prime.Sieve import enumerate_primes

n, step, offset = map(int, sys.stdin.buffer.read().split())
count, values = enumerate_primes(n, step, offset)
print(count, len(values))
print(*values)
