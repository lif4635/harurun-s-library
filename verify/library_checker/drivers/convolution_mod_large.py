import sys
from array import array

from library_codex.convolution.LargeConvolution import multiply


def read_coefficients(stream, n):
    result = array("I", [0]) * n
    count = 0
    value = 0
    active = False
    while True:
        chunk = stream.read(1 << 16)
        if not chunk:
            if active:
                if count >= n:
                    raise ValueError("unexpected number of coefficients")
                result[count] = value
                count += 1
            if count != n:
                raise ValueError("unexpected number of coefficients")
            return result
        for digit in chunk:
            if 48 <= digit <= 57:
                value = value * 10 + digit - 48
                active = True
            elif digit <= 32:
                if active:
                    if count >= n:
                        raise ValueError("unexpected number of coefficients")
                    result[count] = value
                    count += 1
                    value = 0
                    active = False
            else:
                raise ValueError("invalid coefficient")


def main():
    stream = sys.stdin.buffer
    n, m = map(int, stream.readline().split())
    values = read_coefficients(stream, n + m)
    first = values[:n]
    del values[:n]
    result = multiply(first, values)
    for start in range(0, len(result), 8192):
        if start:
            sys.stdout.write(" ")
        sys.stdout.write(" ".join(map(str, result[start:start + 8192])))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
