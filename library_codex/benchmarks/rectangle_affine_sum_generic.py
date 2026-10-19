import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.spatial_structure.LazyKDTree import LazyKDTree


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    xs, ys, values = [], [], []
    for _ in range(n):
        x, y, w = map(int, read().split())
        xs.append(x)
        ys.append(y)
        values.append((w, 1))
    queries = []
    for _ in range(q):
        query = list(map(int, read().split()))
        if query[0] == 0:
            _, x, y, w = query
            query = [1, len(xs), w]
            xs.append(x)
            ys.append(y)
            values.append((0, 0))
        queries.append(query)

    def combine(a, b):
        return (a[0] + b[0]) % 998244353, a[1] + b[1]

    def mapping(value, action, size):
        return (value[0] * action[0] + value[1] * action[1]) % 998244353, value[1]

    def composition(old, new):
        return old[0] * new[0] % 998244353, (old[1] * new[0] + new[1]) % 998244353

    tree = LazyKDTree(xs, ys, values, combine, (0, 0), mapping, composition, (1, 0))
    answer = []
    for query in queries:
        if query[0] == 1:
            _, index, value = query
            tree.set(index, (value, 1))
        elif query[0] == 2:
            _, left, down, right, up = query
            answer.append(str(tree.query(left, right, down, up)[0]))
        else:
            _, left, down, right, up, a, b = query
            tree.update(left, right, down, up, (a, b))
    sys.stdout.write("\n".join(answer) + "\n")


if __name__ == "__main__":
    main()
