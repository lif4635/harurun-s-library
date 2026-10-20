import sys
from array import array

from library_codex.convolution.LargeConvolution import multiply


def read_coefficients(stream, n):
    result = array("I")
    carry = b""
    while len(result) < n:
        chunk = stream.read(1 << 16)
        if not chunk:
            result.extend(map(int, carry.split()))
            break
        chunk = carry + chunk
        end = len(chunk)
        while end and chunk[end - 1] > 32:
            end -= 1
        result.extend(map(int, chunk[:end].split()))
        carry = chunk[end:]
    if len(result) != n:
        raise ValueError("unexpected number of coefficients")
    return result


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
