import sys

from library_codex.convolution.BinaryFieldConvolution import multiply


def main():
    stream = sys.stdin.buffer
    n, m = map(int, stream.readline().split())
    a = list(map(int, stream.readline().split()))
    b = list(map(int, stream.readline().split()))
    if len(a) != n or len(b) != m:
        raise ValueError("unexpected number of coefficients")
    result = multiply(a, b)
    for start in range(0, len(result), 8192):
        if start:
            sys.stdout.write(" ")
        sys.stdout.write(" ".join(map(str, result[start:start + 8192])))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
