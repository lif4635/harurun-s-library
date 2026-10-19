import sys

from library_codex.number_theory.MultiplicativeFunctions import MultiplicativePrefixSum


def main():
    read = sys.stdin.buffer.readline
    mod = 469762049
    output = []
    for _ in range(int(read())):
        n, a, b = map(int, read().split())
        engine = MultiplicativePrefixSum(n, mod)
        counts = engine.prime_count_table() if a else [0] * engine.size
        sums = engine.prime_sum_table() if b else [0] * engine.size
        prefix = [(a * x + b * y) % mod for x, y in zip(counts, sums)]
        output.append(str(engine.run(prefix, lambda p, e: (a * e + b * p) % mod)))
    sys.stdout.write("\n".join(output))


if __name__ == "__main__":
    main()
