import sys

from library_codex.prime.Sieve import sum_totient

print(sum_totient(int(sys.stdin.buffer.read()), 998244353))
