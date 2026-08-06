"""一般の2列に対するmin-plus畳み込みを計算する。"""


def minplus_conv(first, second):
    """Return the full min-plus convolution of two sequences."""
    if not first or not second:
        return []
    output = [float("inf")] * (len(first) + len(second) - 1)
    for first_index, first_value in enumerate(first):
        for second_index, second_value in enumerate(second):
            index = first_index + second_index
            value = first_value + second_value
            if value < output[index]:
                output[index] = value
    return output
