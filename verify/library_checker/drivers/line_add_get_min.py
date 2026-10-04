import sys

from library_codex.spatial_structure.LiChaoTree import LiChaoTree


def solve():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    lines = [tuple(map(int, read().split())) for _ in range(n)]
    queries = [tuple(map(int, read().split())) for _ in range(q)]
    tree = LiChaoTree([query[1] for query in queries if query[0] == 1] or [0])
    for a, b in lines:
        tree.add_line(a, b)
    answer = []
    for query in queries:
        if query[0] == 0:
            tree.add_line(query[1], query[2])
        else:
            answer.append(str(tree.query(query[1])))
    print("\n".join(answer))


if __name__ == "__main__":
    solve()
