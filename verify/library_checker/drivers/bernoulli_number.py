import sys
from library_codex.combinatorial_series.BernoulliNumbers import bernoulli_numbers


def main():
    n = int(sys.stdin.buffer.readline())
    result = bernoulli_numbers(n)
    sys.stdout.write(" ".join(map(str, result)) + "\n")


if __name__ == "__main__":
    main()
