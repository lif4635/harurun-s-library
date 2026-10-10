import sys

from library_codex.graph_connectivity.TreeDecompositionWidth2 import tree_decomposition_width2


read = sys.stdin.buffer.readline
_, _, n, m = read().split()
n, m = int(n), int(m)
edges = ((int(a) - 1, int(b) - 1) for a, b in (read().split() for _ in range(m)))
result = tree_decomposition_width2(n, edges)
if result is None:
    print(-1)
else:
    bags, parent = result
    lines = [f"s td {n} 2 {n}"]
    for i, bag in enumerate(bags):
        lines.append(f"b {i + 1} " + " ".join(str(v + 1) for v in bag))
    lines.extend(f"{i + 1} {p + 1}" for i, p in enumerate(parent) if p >= 0)
    sys.stdout.write("\n".join(lines) + "\n")
