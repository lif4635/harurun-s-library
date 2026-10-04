import sys
from library_codex.combinatorial_series.DerangementNumbers import derangement_numbers


def main():
    n, mod = map(int, sys.stdin.buffer.readline().split())
    sys.stdout.write(" ".join(map(str, derangement_numbers(n, mod)[1:])) + "\n")


if __name__ == "__main__":
    main()
