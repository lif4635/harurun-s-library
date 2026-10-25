"""子孫を参照するマージ用に、構築・一点更新・右からの区間結合を行う。"""


def build(size, pull):
    """葉を配置済みの木を、子から親の順にpull(node)で構築する。"""
    if size < 1 or size & (size - 1):
        raise ValueError("size must be a positive power of two")
    for node in range(size - 1, 0, -1):
        pull(node)


def update(size, index, pull):
    """変更済みの葉indexから根まで、親の情報をpull(node)で再計算する。"""
    if not 0 <= index < size:
        raise IndexError("index outside leaves")
    node = (size + index) >> 1
    while node:
        pull(node)
        node >>= 1


def fold(size, left, right, prepend, initial):
    """半開区間[left, right)を右から結合し、prepend(node, result)の累積値を返す。"""
    if not 0 <= left <= right <= size:
        raise IndexError("invalid half-open range")
    left += size
    right += size
    result = initial
    while left < right:
        height = min((right & -right).bit_length(), (right - left).bit_length()) - 1
        result = prepend((right >> height) - 1, result)
        right -= 1 << height
    return result
