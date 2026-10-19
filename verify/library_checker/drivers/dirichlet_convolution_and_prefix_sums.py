import sys

from library_codex.number_theory.MultiplicativeFunctions import DirichletQuotientSeries, dirichlet_multiply


def main():
    read = sys.stdin.buffer.readline
    write = sys.stdout.write
    for _ in range(int(read())):
        n = int(read())
        a = DirichletQuotientSeries(n, [0] + list(map(int, read().split())), 998244353)
        b = DirichletQuotientSeries(n, [0] + list(map(int, read().split())), 998244353)
        write(" ".join(map(str, dirichlet_multiply(a, b).data[1:])) + "\n")


if __name__ == "__main__":
    main()
