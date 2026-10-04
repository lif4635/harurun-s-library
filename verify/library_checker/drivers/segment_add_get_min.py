import sys

from library_codex.spatial_structure.LiChaoTree import LiChaoTree


def solve():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    segments = [tuple(map(int, read().split())) for _ in range(n)]
    queries = [tuple(map(int, read().split())) for _ in range(q)]
    tree = LiChaoTree([query[1] for query in queries if query[0] == 1] or [0])
    for l, r, a, b in segments:
        tree.add_segment(a, b, l, r)
    answer = []
    for query in queries:
        if query[0] == 0:
            _, l, r, a, b = query
            tree.add_segment(a, b, l, r)
        else:
            value = tree.query(query[1])
            answer.append("INFINITY" if value == float("inf") else str(value))
    print("\n".join(answer))


if __name__ == "__main__":
    solve()
