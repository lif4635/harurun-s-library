import sys
from library_codex.geometry.ArgumentSort import argument_sort


def main():
    read = sys.stdin.buffer.readline
    points = [tuple(map(int, read().split())) for _ in range(int(read()))]
    ordered = argument_sort(points)
    split = next((i for i, point in enumerate(ordered) if point[1] < 0), len(ordered))
    ordered = ordered[split:] + ordered[:split]
    sys.stdout.write("\n".join(f"{x} {y}" for x, y in ordered))


if __name__ == "__main__":
    main()
