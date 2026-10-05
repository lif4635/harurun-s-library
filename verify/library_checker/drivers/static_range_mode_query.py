import sys

from library_codex.range_query.StaticRangeMode import StaticRangeMode


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    table = StaticRangeMode(list(map(int, read().split())))
    result = []
    for _ in range(q):
        left, right = map(int, read().split())
        value, count = table.mode(left, right)
        result.append(f"{value} {count}")
    sys.stdout.write("\n".join(result))


if __name__ == "__main__":
    main()
