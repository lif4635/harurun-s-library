from pathlib import Path
import inspect
import random
import sys


def make_case(problem, size, family, seed):
    from library_codex.benchmarks.lc_problems import PROBLEMS, problem_module

    if problem in PROBLEMS:
        module = problem_module(problem)
        if not getattr(module, "MIN_SIZE", 1) <= size <= getattr(module, "MAX_SIZE", 500000):
            raise ValueError("size is outside the problem constraints")
        if family not in module.FAMILIES:
            raise ValueError("unknown family: " + family)
        return module.make_case(size, family, seed)
    rng = random.Random(seed)
    answers = [] if size <= 256 else None
    if problem == "set_xor_min":
        limits = {"random": 1 << 30, "dense": size * 2, "duplicates": 128, "prefix": 1 << 16}
        if family not in limits:
            raise ValueError("unknown xor family: " + family)
        offset = 1 << 29 if family == "prefix" else 0
        active = set()
        bag = []
        positions = {}
        lines = [str(size)]
        for i in range(size):
            kind = 0 if i < size // 4 or not active else rng.choices([0, 1, 2], [4, 2, 4])[0]
            x = offset + rng.randrange(limits[family])
            if kind == 1 and rng.randrange(4):
                x = bag[rng.randrange(len(bag))]
            lines.append(f"{kind} {x}")
            if kind == 0 and x not in active:
                active.add(x)
                positions[x] = len(bag)
                bag.append(x)
            elif kind == 1 and x in active:
                active.remove(x)
                index = positions.pop(x)
                last = bag.pop()
                if index < len(bag):
                    bag[index] = last
                    positions[last] = index
            elif kind == 2 and answers is not None:
                answers.append(str(min(x ^ y for y in active)).encode())
        return ("\n".join(lines) + "\n").encode(), answers
    if problem != "vertex_add_subtree_sum":
        raise ValueError("unknown problem")
    if family not in {"random", "chain", "star", "balanced"}:
        raise ValueError("unknown tree family: " + family)
    parents = [rng.randrange(v) if family == "random" else v - 1 if family == "chain"
               else 0 if family == "star" else (v - 1) // 2 for v in range(1, size)]
    values = [rng.randrange(1000) for _ in range(size)]
    children = [[] for _ in range(size)]
    for v, p in enumerate(parents, 1):
        children[p].append(v)
    lines = [f"{size} {size}", " ".join(map(str, values)), " ".join(map(str, parents))]
    for i in range(size):
        v = 0 if i % 127 == 0 else rng.randrange(size)
        if rng.randrange(2):
            x = rng.randrange(1000)
            lines.append(f"0 {v} {x}")
            values[v] += x
        else:
            lines.append(f"1 {v}")
            if answers is not None:
                nodes = [v]
                for u in nodes:
                    nodes.extend(children[u])
                answers.append(str(sum(values[u] for u in nodes)).encode())
    return ("\n".join(lines) + "\n").encode(), answers


def solve(problem):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from library_codex.ordered_set.BinaryTrie import BinaryTrie
    from library_codex.fenwick_tree.BIT import BIT
    from library_codex.tree.HeavyLightDecomposition import HeavyLightDecomposition
    from library_codex.tree.DSUOnTree import DSUOnTree

    read = sys.stdin.buffer.readline
    answers = []
    if problem == "set_xor_min":
        q = int(read())
        tree = BinaryTrie()
        for _ in range(q):
            kind, x = map(int, read().split())
            if kind == 0:
                if x not in tree:
                    tree.add(x)
            elif kind == 1:
                tree.discard(x)
            else:
                answers.append(tree.xor_min(x) ^ x)
    else:
        n, q = map(int, read().split())
        values = list(map(int, read().split()))
        parents = list(map(int, read().split()))
        tree = [[] for _ in range(n)]
        for v, p in enumerate(parents, 1):
            tree[p].append(v)
            tree[v].append(p)
        if problem == "subtree_dsu":
            changes = [[(0, values[v])] for v in range(n)]
            queries = [[] for _ in range(n)]
            answers = [None] * (q + 1)
            for t in range(1, q + 1):
                row = list(map(int, read().split()))
                if row[0] == 0:
                    changes[row[1]].append((t, row[2]))
                else:
                    queries[row[1]].append(t)
            bit = BIT(q + 1)

            def add(v):
                for t, x in changes[v]:
                    bit.add(t, x)

            def remove(v):
                for t, x in changes[v]:
                    bit.add(t, -x)

            def query(v):
                for t in queries[v]:
                    answers[t] = bit.prefix_sum(t + 1)

            DSUOnTree(tree).run(add, query, remove)
            answers = [x for x in answers if x is not None]
        else:
            hld = HeavyLightDecomposition(tree)
            bit = BIT([values[v] for v in hld.rev])
            for _ in range(q):
                row = list(map(int, read().split()))
                if row[0] == 0:
                    bit.add(hld.tin[row[1]], row[2])
                else:
                    v = row[1]
                    answers.append(bit.sum(hld.tin[v], hld.tout[v]))
    sys.stdout.write("\n".join(map(str, answers)) + "\n")


def standalone_source(problem):
    from library_codex.benchmarks.lc_problems import PROBLEMS, standalone

    if problem in PROBLEMS:
        return standalone(problem)
    root = Path(__file__).resolve().parents[1]
    modules = ["ordered_set/BinaryTrie.py"] if problem == "set_xor_min" else [
        "fenwick_tree/BIT.py", "tree/DSUOnTree.py" if problem == "subtree_dsu"
        else "tree/HeavyLightDecomposition.py"]
    body = "\n".join(line for line in inspect.getsource(solve).splitlines()
                     if not line.startswith("    from library_codex.")
                     and not line.startswith("    sys.path.insert"))
    return ("\n".join((root / name).read_text() for name in modules)
            + "\nimport sys\n" + body + "\nsolve(" + repr(problem) + ")\n").encode()


if __name__ == "__main__":
    solve(sys.argv[1])
