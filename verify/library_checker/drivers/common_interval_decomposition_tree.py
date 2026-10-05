import sys

from library_codex.algorithm.PermutationTree import PermutationTree


def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    tree = PermutationTree(list(map(int, read().split())))
    order = [tree.root]
    for node in order:
        order.extend(tree.children(node))
    index = [0] * tree.node_count
    for i, node in enumerate(order):
        index[node] = i
    result = [str(tree.node_count)]
    for node in order:
        parent = tree.parent[node]
        parent = -1 if parent < 0 else index[parent]
        kind = "prime" if tree.kind[node] == tree.PRIME else "linear"
        result.append(f"{parent} {tree.left[node]} {tree.right[node] - 1} {kind}")
    sys.stdout.write("\n".join(result))


if __name__ == "__main__":
    main()
