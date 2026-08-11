"""有限列の集合分割を重複なく列挙する。"""


def set_partitions(values, block_count=None):
    """restricted growth string順でblock listを生成する。"""
    values = list(values)
    n = len(values)
    if block_count is not None and not 0 <= block_count <= n:
        return
    if n == 0:
        if block_count in (None, 0):
            yield []
        return
    if block_count == 0:
        return
    labels = [0] * n
    while True:
        count = max(labels) + 1
        if block_count is None or count == block_count:
            blocks = [[] for _ in range(count)]
            for value, label in zip(values, labels):
                blocks[label].append(value)
            yield blocks
        index = n - 1
        while index:
            limit = max(labels[:index]) + 1
            if block_count is not None and limit >= block_count:
                limit = block_count - 1
            if labels[index] < limit:
                labels[index] += 1
                labels[index + 1:] = [0] * (n - index - 1)
                break
            index -= 1
        if index == 0:
            return
