import sys
from library_codex.geometry.ClosestPair import closest_pair


def main():
    read = sys.stdin.buffer.readline
    answer = []
    for _ in range(int(read())):
        points = [tuple(map(int, read().split())) for _ in range(int(read()))]
        first, second, distance = closest_pair(points)
        answer.append(f"{first} {second}")
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
