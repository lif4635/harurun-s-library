import sys
from library_codex.combinatorial_series.StirlingNumbers import stirling_first_row


def main():
    n = int(sys.stdin.buffer.readline())
    result = stirling_first_row(n, signed=True)
    sys.stdout.write(" ".join(map(str, result)) + "\n")


if __name__ == "__main__":
    main()
