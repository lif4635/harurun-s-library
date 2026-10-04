import sys
from library_codex.arithmetic_convolution.ArithmeticConvolution import lcm_convolution


def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    a = [0] + list(map(int, read().split()))
    b = [0] + list(map(int, read().split()))
    sys.stdout.write(" ".join(map(str, lcm_convolution(a, b)[1:])) + "\n")


if __name__ == "__main__":
    main()
