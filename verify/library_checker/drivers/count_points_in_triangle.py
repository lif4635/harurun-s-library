import sys

from library_codex.geometry.TrianglePointCounter import TrianglePointCounter


def main():
    read = sys.stdin.buffer.readline
    vertices = [tuple(map(int, read().split())) for _ in range(int(read()))]
    points = [tuple(map(int, read().split())) for _ in range(int(read()))]
    counter = TrianglePointCounter(vertices, points)
    count = counter.count
    answer = []
    for _ in range(int(read())):
        a, b, c = map(int, read().split())
        answer.append(str(count(a, b, c)))
    sys.stdout.write("\n".join(answer) + "\n")


if __name__ == "__main__":
    main()
