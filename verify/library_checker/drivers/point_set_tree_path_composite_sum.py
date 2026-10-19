import sys

from library_codex.tree.TreePathCompositeSum import TreePathCompositeSum


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    values = list(map(int, read().split()))
    edges = [tuple(map(int, read().split())) for _ in range(n - 1)]
    tree = TreePathCompositeSum(values, edges)
    answer = []
    for _ in range(q):
        query = list(map(int, read().split()))
        if query[0] == 0:
            _, vertex, value, root = query
            tree.set(vertex, value)
        else:
            _, edge, b, c, root = query
            tree.set_edge(edge, b, c)
        answer.append(str(tree.query(root)))
    sys.stdout.write("\n".join(answer) + "\n")


if __name__ == "__main__":
    main()
