import sys

from library_codex.fps998.SubsetSum import subset_sum


def main():
    read = sys.stdin.buffer.readline
    n, limit = map(int, read().split())
    counts = [0] * (limit + 1)
    for value in map(int, read().split()):
        counts[value] += 1
    result = subset_sum(counts)
    sys.stdout.write(" ".join(map(str, result[1:])) + "\n")


if __name__ == "__main__":
    main()
