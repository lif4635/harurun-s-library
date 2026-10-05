import sys

from library_codex.number_theory.TwoSquareRepresentations import two_square_representations


def main():
    read = sys.stdin.buffer.readline
    result = []
    for _ in range(int(read())):
        pairs = two_square_representations(int(read()))
        result.append(str(len(pairs)))
        result.extend(f"{a} {b}" for a, b in pairs)
    sys.stdout.write("\n".join(result))


if __name__ == "__main__":
    main()
