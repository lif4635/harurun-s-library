import sys

from library_codex.range_query.WeightedWaveletMatrix import WeightedWaveletMatrix


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    table = WeightedWaveletMatrix(list(map(int, read().split())))
    result = []
    for _ in range(q):
        left, right, upper = map(int, read().split())
        count, total = table.count_sum_lt(left, right, upper + 1)
        result.append(f"{count} {total}")
    sys.stdout.write("\n".join(result))


if __name__ == "__main__":
    main()
