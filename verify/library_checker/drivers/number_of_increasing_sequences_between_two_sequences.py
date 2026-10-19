import sys

from library_codex.fps.IncreasingSequences import count_increasing_sequences


def main():
    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    lower = list(map(int, read().split()))
    upper = list(map(int, read().split()))
    print(count_increasing_sequences(lower, upper))


if __name__ == "__main__":
    main()
