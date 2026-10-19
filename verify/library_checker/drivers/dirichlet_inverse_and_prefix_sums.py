import sys

from library_codex.number_theory.MultiplicativeFunctions import DirichletQuotientSeries, dirichlet_divide


def main():
    read = sys.stdin.buffer.readline
    write = sys.stdout.write
    for _ in range(int(read())):
        n = int(read())
        a = DirichletQuotientSeries(n, [0] + list(map(int, read().split())), 998244353)
        unit = DirichletQuotientSeries(n, [0] + [1] * (a.size - 1), 998244353)
        write(" ".join(map(str, dirichlet_divide(unit, a).data[1:])) + "\n")


if __name__ == "__main__":
    main()
