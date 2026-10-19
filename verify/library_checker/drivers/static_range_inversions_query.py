import sys

from library_codex.range_query.OfflineRangeInversions import range_inversions


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    values = list(map(int, read().split()))
    queries = [tuple(map(int, read().split())) for _ in range(q)]
    sys.stdout.write("\n".join(map(str, range_inversions(values, queries))))


if __name__ == "__main__":
    main()
