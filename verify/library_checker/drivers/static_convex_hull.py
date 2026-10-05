import sys
from library_codex.geometry.ConvexHull import convex_hull


def main():
    read = sys.stdin.buffer.readline
    answer = []
    for _ in range(int(read())):
        points = [tuple(map(int, read().split())) for _ in range(int(read()))]
        hull = convex_hull(points)
        answer.append(str(len(hull)))
        answer.extend(f"{x} {y}" for x, y in hull)
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
