import sys

from library_codex.spatial_structure.RectangleAffineSum import RectangleAffineSum


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    points = [tuple(map(int, read().split())) for _ in range(n)]
    queries = []
    for _ in range(q):
        query = list(map(int, read().split()))
        if query[0] == 0:
            _, x, y, w = query
            query = [1, len(points), w]
            points.append((x, y, None))
        queries.append(query)
    tree = RectangleAffineSum(points)
    answer = []
    for query in queries:
        if query[0] == 1:
            _, index, value = query
            tree.set(index, value)
        elif query[0] == 2:
            _, left, down, right, up = query
            answer.append(str(tree.sum(left, right, down, up)))
        else:
            _, left, down, right, up, a, b = query
            tree.apply(left, right, down, up, a, b)
    sys.stdout.write("\n".join(answer) + "\n")


if __name__ == "__main__":
    main()
