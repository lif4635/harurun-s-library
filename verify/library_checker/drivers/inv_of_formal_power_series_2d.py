import sys
from library_codex.fps.MultivariateFPS import MultivariateFormalPowerSeries


def main():
    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    series = []
    for _ in range(n):
        series.extend(map(int, read().split()))
    result = MultivariateFormalPowerSeries(series, (m, n)).inverse().coefficients
    write = sys.stdout.write
    for i in range(0, n * m, m):
        write(" ".join(map(str, result[i:i + m])) + "\n")


if __name__ == "__main__":
    main()
