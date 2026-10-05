import sys

from library_codex.combinatorics.Combination import Comb


def main():
    read = sys.stdin.buffer.readline
    count, mod = map(int, read().split())
    data = list(map(int, sys.stdin.buffer.read().split()))
    maximum = max(data[::2], default=0)
    comb = Comb(maximum, mod)
    result = [str(comb.C(data[i], data[i + 1])) for i in range(0, count * 2, 2)]
    sys.stdout.write("\n".join(result))


if __name__ == "__main__":
    main()
