from collections import deque
import random
import subprocess
import sys

import pytest

from library_codex.tree.LinkCutTree import (
    LazyLinkCutTree,
    LinkCutTree,
    SubtreeAddLinkCutTree,
    SubtreeLinkCutTree,
)


def find_path(graph, start, goal):
    parent = [-2] * len(graph)
    parent[start] = -1
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == goal:
            result = []
            while node >= 0:
                result.append(node)
                node = parent[node]
            result.reverse()
            return result
        for other in graph[node]:
            if parent[other] == -2:
                parent[other] = node
                queue.append(other)
    return None


def rooted_subtree(graph, root, node):
    parent = [-2] * len(graph)
    parent[root] = -1
    stack = [root]
    while stack:
        current = stack.pop()
        for other in graph[current]:
            if other != parent[current]:
                parent[other] = current
                stack.append(other)
    result = []
    stack = [node]
    while stack:
        current = stack.pop()
        result.append(current)
        for other in graph[current]:
            if parent[other] == current:
                stack.append(other)
    return result


def random_forest_step(rng, graph, solver):
    n = len(graph)
    edges = [
        (node, other)
        for node in range(n)
        for other in graph[node]
        if node < other
    ]
    if edges and rng.randrange(3) == 0:
        first, second = rng.choice(edges)
        assert solver.cut(first, second)
        graph[first].remove(second)
        graph[second].remove(first)
        return
    for _ in range(30):
        first = rng.randrange(n)
        second = rng.randrange(n)
        if first != second and find_path(graph, first, second) is None:
            assert solver.link(first, second)
            graph[first].add(second)
            graph[second].add(first)
            return


def test_link_cut_tree_random_dynamic_forest():
    rng = random.Random(927531)
    n = 22
    values = [rng.randrange(-20, 21) for _ in range(n)]
    solver = LinkCutTree(values)
    graph = [set() for _ in range(n)]
    for step in range(6000):
        kind = rng.randrange(6)
        if kind == 0:
            random_forest_step(rng, graph, solver)
        elif kind == 1:
            node = rng.randrange(n)
            value = rng.randrange(-100, 101)
            values[node] = value
            solver.set_value(node, value)
        else:
            first = rng.randrange(n)
            second = rng.randrange(n)
            path = find_path(graph, first, second)
            assert solver.connected(first, second) == (path is not None)
            if path is not None:
                assert solver.path_fold(first, second) == sum(
                    values[node] for node in path
                )
                assert solver.path_length(first, second) == len(path)
                index = rng.randrange(len(path))
                assert solver.kth_on_path(first, second, index) == path[index]
                assert solver.get_kth(second, index) == path[-1 - index]


def test_link_cut_tree_noncommutative_direction_and_lca():
    graph = [set() for _ in range(9)]
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (5, 6), (5, 7), (7, 8)]
    values = list("abcdefghi")
    solver = LinkCutTree(values, lambda x, y: x + y, "")
    for first, second in edges:
        graph[first].add(second)
        graph[second].add(first)
        assert solver.link(first, second)
    for first in range(9):
        for second in range(9):
            path = find_path(graph, first, second)
            assert solver.path_fold(first, second) == "".join(
                values[node] for node in path
            )
    assert solver.lca(3, 8, root=0) == 0
    assert solver.lca(6, 8, root=0) == 5
    assert solver.parent_of(7, root=0) == 5
    assert solver.parent_of(0, root=0) == -1


def test_lazy_link_cut_tree_random_path_add_sum():
    rng = random.Random(81642)
    n = 24
    values = [rng.randrange(-10, 11) for _ in range(n)]
    solver = LazyLinkCutTree(
        values,
        lambda x, y: x + y,
        0,
        lambda action, aggregate, length: aggregate + action * length,
        lambda new, old: new + old,
    )
    graph = [set() for _ in range(n)]
    for _ in range(5000):
        kind = rng.randrange(6)
        if kind == 0:
            random_forest_step(rng, graph, solver)
            continue
        first = rng.randrange(n)
        second = rng.randrange(n)
        path = find_path(graph, first, second)
        if path is None:
            continue
        if kind <= 2:
            delta = rng.randrange(-10, 11)
            solver.path_apply(first, second, delta)
            for node in path:
                values[node] += delta
        else:
            assert solver.path_fold(first, second) == sum(
                values[node] for node in path
            )
            node = rng.choice(path)
            assert solver.get_value(node) == values[node]


def test_subtree_link_cut_tree_random_dynamic_forest():
    rng = random.Random(571902)
    n = 20
    values = [rng.randrange(-50, 51) for _ in range(n)]
    solver = SubtreeLinkCutTree(values)
    graph = [set() for _ in range(n)]
    for _ in range(5000):
        kind = rng.randrange(5)
        if kind == 0:
            random_forest_step(rng, graph, solver)
        elif kind == 1:
            node = rng.randrange(n)
            value = rng.randrange(-50, 51)
            values[node] = value
            solver.set_value(node, value)
        else:
            root = rng.randrange(n)
            component = [
                node for node in range(n) if find_path(graph, root, node)
            ]
            node = rng.choice(component)
            subtree = rooted_subtree(graph, root, node)
            assert solver.subtree_fold(node, root) == sum(
                values[vertex] for vertex in subtree
            )
            assert solver.component_fold(node) == sum(
                values[vertex] for vertex in component
            )


def test_subtree_add_link_cut_tree_random_dynamic_forest():
    rng = random.Random(420613)
    n = 18
    values = [rng.randrange(-30, 31) for _ in range(n)]
    solver = SubtreeAddLinkCutTree(values)
    graph = [set() for _ in range(n)]
    for _ in range(6000):
        kind = rng.randrange(6)
        if kind == 0:
            random_forest_step(rng, graph, solver)
            continue
        root = rng.randrange(n)
        component = [
            node for node in range(n) if find_path(graph, root, node)
        ]
        node = rng.choice(component)
        subtree = rooted_subtree(graph, root, node)
        if kind <= 2:
            delta = rng.randrange(-20, 21)
            solver.subtree_add(node, delta, root)
            for vertex in subtree:
                values[vertex] += delta
        elif kind == 3:
            value = rng.randrange(-50, 51)
            values[node] = value
            solver.set_value(node, value)
        else:
            assert solver.subtree_sum(node, root) == sum(
                values[vertex] for vertex in subtree
            )
            assert solver.component_sum(node) == sum(
                values[vertex] for vertex in component
            )


def test_link_cut_tree_deep_path_without_recursion():
    n = 30000
    solver = LinkCutTree(range(n))
    for node in range(n - 1):
        assert solver.link(node, node + 1)
    assert solver.path_fold(0, n - 1) == n * (n - 1) // 2
    assert solver.kth_on_path(n - 1, 0, n // 3) == n - 1 - n // 3
    for node in range(1, n, 3):
        assert solver.cut(node - 1, node)
        assert not solver.connected(node - 1, node)


@pytest.mark.parametrize("factory", [LinkCutTree, SubtreeLinkCutTree, SubtreeAddLinkCutTree])
def test_link_rejects_cycles_after_root_changes(factory):
    tree = factory([2, 3, 5, 7, 11])
    for vertex in range(4):
        assert tree.link(vertex, vertex + 1)
    for root in range(5):
        tree.make_root(root)
        for u in range(5):
            for v in range(5):
                assert not tree.link(u, v)
                assert tree.connected(u, v)
    assert tree.cut(1, 2)
    assert tree.link(0, 4)
    assert not tree.link(0, 4)
    assert tree.connected(1, 2)


@pytest.mark.parametrize("problem", [
    "dynamic_tree_vertex_add_path_sum",
    "dynamic_tree_vertex_set_path_composite",
    "dynamic_tree_vertex_add_subtree_sum",
    "dynamic_tree_subtree_add_subtree_sum",
])
def test_library_checker_dynamic_tree_drivers(problem, tmp_path):
    from library_codex.tools.check_library_checker import solution

    rng = random.Random(638214)
    n, q = 19, 700
    affine = problem.endswith("path_composite")
    path_query = "path" in problem
    subtree_add = problem == "dynamic_tree_subtree_add_subtree_sum"
    values = [(rng.randrange(1, 100), rng.randrange(100)) for _ in range(n)] if affine else [rng.randrange(100) for _ in range(n)]
    lines = [f"{n} {q}"]
    if affine:
        lines.extend(f"{a} {b}" for a, b in values)
    else:
        lines.append(" ".join(map(str, values)))
    graph = [set() for _ in range(n)]
    edges = []
    for v in range(1, n):
        p = rng.randrange(v)
        edges.append((v, p))
        graph[v].add(p)
        graph[p].add(v)
        lines.append(f"{v} {p}")
    expected = []
    for step in range(q):
        kind = step % 3
        if kind == 0:
            index = rng.randrange(n - 1)
            u, v = edges[index]
            graph[u].remove(v)
            graph[v].remove(u)
            component = [x for x in range(n) if find_path(graph, u, x) is not None]
            other = [x for x in range(n) if x not in component]
            w, x = rng.choice(component), rng.choice(other)
            graph[w].add(x)
            graph[x].add(w)
            edges[index] = w, x
            lines.append(f"0 {u} {v} {w} {x}")
        elif kind == 1:
            v = rng.randrange(n)
            x = rng.randrange(100)
            if affine:
                a = rng.randrange(1, 100)
                values[v] = a, x
                lines.append(f"1 {v} {a} {x}")
            elif subtree_add:
                p = rng.choice(sorted(graph[v]))
                for u in rooted_subtree(graph, p, v):
                    values[u] += x
                lines.append(f"1 {v} {p} {x}")
            else:
                values[v] += x
                lines.append(f"1 {v} {x}")
        else:
            u = rng.randrange(n)
            v = rng.randrange(n) if path_query else rng.choice(sorted(graph[u]))
            vertices = find_path(graph, u, v) if path_query else rooted_subtree(graph, v, u)
            if affine:
                x = rng.randrange(998244353)
                lines.append(f"2 {u} {v} {x}")
                for vertex in vertices:
                    a, b = values[vertex]
                    x = (a * x + b) % 998244353
                expected.append(str(x))
            else:
                lines.append(f"2 {u} {v}")
                expected.append(str(sum(values[vertex] for vertex in vertices)))
    source, _ = solution(problem)
    script = tmp_path / "main.py"
    script.write_text(source)
    result = subprocess.run([sys.executable, "-I", str(script)], input="\n".join(lines) + "\n", text=True, capture_output=True, check=True, timeout=30)
    assert result.stdout.split() == expected
