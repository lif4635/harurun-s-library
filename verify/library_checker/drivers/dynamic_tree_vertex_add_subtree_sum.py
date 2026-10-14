import sys

from library_codex.graph_connectivity.OfflineDynamicSum import OfflineDynamicSum


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    tree = OfflineDynamicSum(list(map(int, read().split())))
    for _ in range(n - 1):
        u, v = map(int, read().split())
        tree.add_edge(u, v)
    for _ in range(q):
        query = list(map(int, read().split()))
        if query[0] == 0:
            _, u, v, w, x = query
            tree.remove_edge(u, v)
            tree.add_edge(w, x)
        elif query[0] == 1:
            _, p, x = query
            tree.add(p, x)
        else:
            _, v, p = query
            tree.remove_edge(v, p)
            tree.query(v)
            tree.add_edge(v, p)
    sys.stdout.write("\n".join(map(str, tree.solve())) + "\n")


if __name__ == "__main__":
    main()
