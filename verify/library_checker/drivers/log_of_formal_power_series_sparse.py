import sys
from library_codex.fps998.FPS import fps_log


def main():
    read = sys.stdin.buffer.readline
    n, k = map(int, read().split())
    series = [0] * n
    for _ in range(k):
        index, value = map(int, read().split())
        series[index] = value
    result = fps_log(series)
    sys.stdout.write(" ".join(map(str, result)) + "\n")


if __name__ == "__main__":
    main()
