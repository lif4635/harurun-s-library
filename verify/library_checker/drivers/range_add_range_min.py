import sys

from library_codex.segment_tree.LazySegTree import LazySegTree


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    table = LazySegTree(
        min, 1 << 60, lambda action, value, length: value + action,
        lambda newer, older: newer + older, 0, list(map(int, read().split()))
    )
    result = []
    for _ in range(q):
        row = list(map(int, read().split()))
        if row[0] == 0:
            table.apply(*row[1:])
        else:
            result.append(str(table.prod(row[1], row[2])))
    sys.stdout.write("\n".join(result))


if __name__ == "__main__":
    main()
