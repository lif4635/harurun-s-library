"""整数とGray codeを相互変換する。"""

from collections import deque

def gray_code(value):
    return value ^ (value >> 1)

def inverse_gray_code(value):
    result = 0
    while value:
        result ^= value
        value >>= 1
    return result


def gray_code_path(bit_count, start, goal):
    """startからgoalまで全bitmaskを一度ずつ通るGray code列を返す。O(2^N)。"""
    limit = 1 << bit_count
    if bit_count < 1 or not 0 <= start < limit or not 0 <= goal < limit:
        raise ValueError("bit_count and endpoints are inconsistent")
    if (start ^ goal).bit_count() & 1 == 0:
        raise ValueError("Hamilton path endpoints must have opposite parity")
    code = deque((index ^ (index >> 1)) ^ start for index in range(limit))
    direction = 0
    for index in range(limit):
        direction = (0, -1, -1, 0)[index & 3]
        if code[direction] == goal:
            break
        if direction == 0:
            yield code.popleft()
        else:
            yield code.pop()
    if direction == 0:
        while code:
            yield code.pop()
    else:
        while code:
            yield code.popleft()
