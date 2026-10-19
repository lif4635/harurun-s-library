import sys

from library_codex.geometry.ConvexLayers import onion_depth


def main():
    input = sys.stdin.buffer.readline
    n = int(input())
    points = [tuple(map(int, input().split())) for _ in range(n)]
    sys.stdout.write("\n".join(str(value + 1) for value in onion_depth(points)))


if __name__ == "__main__":
    main()
