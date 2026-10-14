import sys

from library_codex.tree.StaticTopTree import DynamicTreeDP, StaticTopTree


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    values = list(map(int, read().split()))
    graph = [[] for _ in range(n)]
    edges = []
    for _ in range(n - 1):
        u, v, b, c = map(int, read().split())
        graph[u].append(v)
        graph[v].append(u)
        edges.append((u, v, b, c))
    tree = StaticTopTree(graph)
    parent = tree.tree_parent
    size = tree.subtree_size
    multiplier = [1] * n
    constant = [0] * n
    child = []
    for u, v, b, c in edges:
        node = v if parent[v] == u else u
        child.append(node)
        multiplier[node] = b
        constant[node] = c

    def vertex(node):
        b = multiplier[node]
        return b, (b * values[node] + constant[node] * size[node]) % 998244353

    def rake(left, right):
        return left[0], (left[1] + right[1]) % 998244353

    def compress(upper, lower):
        return upper[0] * lower[0] % 998244353, (upper[0] * lower[1] + upper[1]) % 998244353

    dp = DynamicTreeDP(tree, vertex, rake, compress)
    answer = []
    for _ in range(q):
        query = list(map(int, read().split()))
        if query[0] == 0:
            _, node, value = query
            values[node] = value
        else:
            _, edge, b, c = query
            node = child[edge]
            multiplier[node] = b
            constant[node] = c
        dp.set(node, vertex(node))
        answer.append(str(dp.get()[1]))
    sys.stdout.write("\n".join(answer) + "\n")


if __name__ == "__main__":
    main()
