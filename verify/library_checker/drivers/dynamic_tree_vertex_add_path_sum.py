import sys

from library_codex.tree.LinkCutTree import LinkCutTree


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    values = list(map(int, read().split()))
    tree = LinkCutTree(values)
    for _ in range(n - 1):
        u, v = map(int, read().split())
        tree.link(u, v)
    answer = []
    for _ in range(q):
        query = list(map(int, read().split()))
        if query[0] == 0:
            _, u, v, w, x = query
            tree.cut(u, v)
            tree.link(w, x)
        elif query[0] == 1:
            _, p, x = query
            values[p] += x
            tree.set_value(p, values[p])
        else:
            answer.append(str(tree.path_fold(query[1], query[2])))
    sys.stdout.write("\n".join(answer) + "\n")


if __name__ == "__main__":
    main()
