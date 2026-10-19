import sys

from library_codex.combinatorics.FactorialQueries import factorials


def main():
    data = list(map(int, sys.stdin.buffer.read().split()))
    print("\n".join(map(str, factorials(data[1:]))))


if __name__ == "__main__":
    main()
