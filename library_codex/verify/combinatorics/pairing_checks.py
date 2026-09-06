def check_pairing(sequence, n, offset, hooked):
    assert isinstance(sequence, list)
    assert len(sequence) == 2*n + hooked
    positions = [-1] * (n+1)
    counts = [0] * (n+1)
    for i, value in enumerate(sequence):
        assert type(value) is int and 0 <= value <= n
        counts[value] += 1
        if value:
            if positions[value] == -1:
                positions[value] = i
            else:
                assert i - positions[value] == value + offset
    assert counts[1:] == [2] * n
    assert counts[0] == int(hooked)
    if hooked:
        assert sequence[-2] == 0


def brute_exists(n, offset, hooked):
    if not n:
        return not hooked
    length = 2*n + hooked
    occupied = 1 << (length - 2) if hooked else 0
    stack = [(n, occupied)]
    while stack:
        k, occupied = stack.pop()
        if k == 0:
            return True
        for i in range(length - k - offset):
            mask = (1 << i) | (1 << (i + k + offset))
            if occupied & mask == 0:
                stack.append((k-1, occupied | mask))
    return False
