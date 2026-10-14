import sys

from library_codex.combinatorics.ArbitraryBinomial import LargePrimeFactorial


def main():
    read = sys.stdin.buffer.readline
    count = int(read())
    factorial = LargePrimeFactorial(998244353).factorial
    result = [str(factorial(int(read()))) for _ in range(count)]
    sys.stdout.write("\n".join(result) + "\n")


if __name__ == "__main__":
    main()
