import sys
from library_codex.game.Nimber import nim_product64


def main():
    read = sys.stdin.buffer.readline
    output = []
    for _ in range(int(read())):
        a, b = map(int, read().split())
        output.append(str(nim_product64(a, b)))
    sys.stdout.write("\n".join(output) + "\n")


if __name__ == "__main__":
    main()
