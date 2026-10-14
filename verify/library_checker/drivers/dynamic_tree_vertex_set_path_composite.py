import sys

from library_codex.tree.LinkCutTree import LinkCutTree


def compose(first, second):
    a, b = first >> 30, first & 1073741823
    c, d = second >> 30, second & 1073741823
    return (a * c % 998244353) << 30 | (b * c + d) % 998244353


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    values = []
    for _ in range(n):
        a, b = map(int, read().split())
        values.append(a << 30 | b)
    tree = LinkCutTree(values, compose, 1 << 30)
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
            _, p, c, d = query
            tree.set_value(p, c << 30 | d)
        else:
            _, u, v, x = query
            value = tree.path_fold(u, v)
            answer.append(str(((value >> 30) * x + (value & 1073741823)) % 998244353))
    sys.stdout.write("\n".join(answer) + "\n")


if __name__ == "__main__":
    main()
