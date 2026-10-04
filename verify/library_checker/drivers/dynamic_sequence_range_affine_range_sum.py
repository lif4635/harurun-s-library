import sys
from library_codex.sequence_structure.ImplicitTreap import ImplicitTreap


def op(a, b):
    return (a + b) % 998244353


def mapping(f, value, size):
    return ((f >> 32) * value + (f & 0xFFFFFFFF) * size) % 998244353


def composition(f, g):
    a = f >> 32
    return (a * (g >> 32) % 998244353 << 32) | ((a * (g & 0xFFFFFFFF) + (f & 0xFFFFFFFF)) % 998244353)


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    tree = ImplicitTreap(map(int, read().split()), op, 0, mapping, composition, commutative=True)
    answer = []
    for _ in range(q):
        query = list(map(int, read().split()))
        kind = query[0]
        if kind == 0:
            tree.insert(query[1], query[2])
        elif kind == 1:
            tree.pop(query[1])
        elif kind == 2:
            tree.reverse_range(query[1], query[2])
        elif kind == 3:
            tree.apply(query[1], query[2], query[3] << 32 | query[4])
        else:
            answer.append(str(tree.prod(query[1], query[2])))
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
