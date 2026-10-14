import random
import subprocess
import sys

import pytest

from library_codex.tools.check_library_checker import solution


def naive(values, edges, root):
    graph = [[] for _ in values]
    for u, v, b, c in edges:
        graph[u].append((v, b, c))
        graph[v].append((u, b, c))
    result = 0
    stack = [(root, -1, 1, 0)]
    while stack:
        node, parent, a, d = stack.pop()
        result = (result + a * values[node] + d) % 998244353
        for other, b, c in graph[node]:
            if other != parent:
                stack.append((other, node, a * b % 998244353, (a * c + d) % 998244353))
    return result


@pytest.mark.parametrize("dynamic", [False, True])
def test_tree_path_composite_sum_against_naive(tmp_path, dynamic):
    name = "point_set_tree_path_composite_sum_fixed_root" if dynamic else "tree_path_composite_sum"
    source, _ = solution(name)
    script = tmp_path / "main.py"
    script.write_text(source, encoding="utf-8")
    rng = random.Random(20261015)
    for n in (1, 2, 7, 30):
        for shape in ("path", "star", "random"):
            permutation = list(range(n))
            rng.shuffle(permutation)
            values = [rng.randrange(998244353) for _ in range(n)]
            edges = []
            for v in range(1, n):
                u = v - 1 if shape == "path" else 0 if shape == "star" else rng.randrange(v)
                u, v = permutation[u], permutation[v]
                if rng.randrange(2):
                    u, v = v, u
                edges.append([u, v, rng.randrange(998244353), rng.randrange(998244353)])
            rng.shuffle(edges)
            q = 150
            lines = [f"{n} {q}" if dynamic else str(n), " ".join(map(str, values))]
            lines.extend(" ".join(map(str, edge)) for edge in edges)
            expected = []
            if dynamic:
                for _ in range(q):
                    if n == 1 or rng.randrange(2):
                        v = rng.randrange(n)
                        value = rng.choice((0, 1, 998244352, rng.randrange(998244353)))
                        lines.append(f"0 {v} {value}")
                        values[v] = value
                    else:
                        e = rng.randrange(n - 1)
                        b, c = rng.choice((0, 1, 998244352)), rng.randrange(998244353)
                        lines.append(f"1 {e} {b} {c}")
                        edges[e][2:] = [b, c]
                    expected.append(naive(values, edges, 0))
            else:
                expected = [naive(values, edges, root) for root in range(n)]
            result = subprocess.run([sys.executable, "-I", str(script)], input="\n".join(lines) + "\n",
                                    text=True, capture_output=True, check=True, cwd=tmp_path, timeout=20)
            assert list(map(int, result.stdout.split())) == expected
