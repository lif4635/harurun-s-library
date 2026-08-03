"""整数とGray codeを相互変換する。"""

def gray_code(value):
    return value ^ (value >> 1)

def inverse_gray_code(value):
    result = 0
    while value:
        result ^= value
        value >>= 1
    return result

