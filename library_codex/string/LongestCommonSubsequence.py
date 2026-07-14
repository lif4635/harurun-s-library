def _lcs_dp_length(first, second):
    if len(first) < len(second):
        first, second = second, first
    row = [0] * (len(second) + 1)
    for left_value in first:
        diagonal = 0
        for column, right_value in enumerate(second, 1):
            old = row[column]
            if left_value == right_value:
                row[column] = diagonal + 1
            elif row[column - 1] > old:
                row[column] = row[column - 1]
            diagonal = old
    return row[-1]


def lcs_length(first, second):
    if not first or not second:
        return 0
    if len(second) > len(first):
        first, second = second, first
    masks = {}
    try:
        for index, value in enumerate(second):
            masks[value] = masks.get(value, 0) | (1 << index)
        state = 0
        for value in first:
            matches = masks.get(value, 0)
            union = state | matches
            state = union & ~(union - ((state << 1) | 1))
    except TypeError:
        return _lcs_dp_length(first, second)
    return state.bit_count()


def _lcs_row_dp(
    first,
    first_left,
    first_right,
    second,
    second_left,
    second_right,
    reverse,
):
    width = second_right - second_left
    row = [0] * (width + 1)
    if reverse:
        first_range = range(first_right - 1, first_left - 1, -1)
    else:
        first_range = range(first_left, first_right)
    for first_index in first_range:
        value = first[first_index]
        diagonal = 0
        for offset in range(width):
            second_index = (
                second_right - 1 - offset
                if reverse
                else second_left + offset
            )
            column = offset + 1
            old = row[column]
            if value == second[second_index]:
                row[column] = diagonal + 1
            elif row[column - 1] > old:
                row[column] = row[column - 1]
            diagonal = old
    return row


def _lcs_row(
    first,
    first_left,
    first_right,
    second,
    second_left,
    second_right,
    reverse,
):
    width = second_right - second_left
    masks = {}
    try:
        for offset in range(width):
            index = (
                second_right - 1 - offset
                if reverse
                else second_left + offset
            )
            value = second[index]
            masks[value] = masks.get(value, 0) | (1 << offset)
        state = 0
        if reverse:
            first_range = range(first_right - 1, first_left - 1, -1)
        else:
            first_range = range(first_left, first_right)
        for index in first_range:
            matches = masks.get(first[index], 0)
            union = state | matches
            state = union & ~(union - ((state << 1) | 1))
    except TypeError:
        return _lcs_row_dp(
            first,
            first_left,
            first_right,
            second,
            second_left,
            second_right,
            reverse,
        )
    packed = state.to_bytes((width + 7) >> 3, "little")
    row = [0] * (width + 1)
    count = 0
    for offset in range(width):
        count += (packed[offset >> 3] >> (offset & 7)) & 1
        row[offset + 1] = count
    return row


def _pack_like(sequence, values):
    if isinstance(sequence, str):
        return "".join(values)
    if isinstance(sequence, bytes):
        return bytes(values)
    if isinstance(sequence, bytearray):
        return bytearray(values)
    if isinstance(sequence, tuple):
        return tuple(values)
    return values


def restore_lcs(first, second):
    original = first
    if len(second) > len(first):
        first, second = second, first
    result = []
    stack = [(0, len(first), 0, len(second))]
    while stack:
        first_left, first_right, second_left, second_right = stack.pop()
        if first_left == first_right or second_left == second_right:
            continue
        if first_right - first_left == 1:
            value = first[first_left]
            for index in range(second_left, second_right):
                if second[index] == value:
                    result.append(value)
                    break
            continue
        if second_right - second_left == 1:
            value = second[second_left]
            for index in range(first_left, first_right):
                if first[index] == value:
                    result.append(value)
                    break
            continue

        middle = (first_left + first_right) >> 1
        forward = _lcs_row(
            first,
            first_left,
            middle,
            second,
            second_left,
            second_right,
            False,
        )
        backward = _lcs_row(
            first,
            middle,
            first_right,
            second,
            second_left,
            second_right,
            True,
        )
        width = second_right - second_left
        split_offset = 0
        best = -1
        for offset in range(width + 1):
            value = forward[offset] + backward[width - offset]
            if value > best:
                best = value
                split_offset = offset
        second_middle = second_left + split_offset
        stack.append((middle, first_right, second_middle, second_right))
        stack.append((first_left, middle, second_left, second_middle))
    return _pack_like(original, result)


longest_common_subsequence = restore_lcs
LCS = lcs_length
restoreLCS = restore_lcs
