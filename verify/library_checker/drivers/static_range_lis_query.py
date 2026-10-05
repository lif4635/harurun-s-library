import sys

from library_codex.segment_tree.RangeLIS import RangeLIS


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    table = RangeLIS(list(map(int, read().split())))
    result = []
    for _ in range(q):
        left, right = map(int, read().split())
        result.append(str(table.query(left, right)))
    sys.stdout.write("\n".join(result))


if __name__ == "__main__":
    main()
