import sys

from library_codex.segment_tree.SegmentTreeBeats import SegmentTreeBeats


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    tree = SegmentTreeBeats(list(map(int, read().split())))
    result = []
    for _ in range(q):
        query = list(map(int, read().split()))
        kind, left, right = query[:3]
        if kind == 0:
            tree.range_chmin(left, right, query[3])
        elif kind == 1:
            tree.range_chmax(left, right, query[3])
        elif kind == 2:
            tree.range_add(left, right, query[3])
        else:
            result.append(str(tree.range_sum(left, right)))
    sys.stdout.write("\n".join(result))


if __name__ == "__main__":
    main()
