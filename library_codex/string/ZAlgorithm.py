def z_algorithm(sequence):
    n = len(sequence)
    if n == 0:
        return []
    z = [0] * n
    z[0] = n
    i = 1
    matched = 0
    while i < n:
        while (
            i + matched < n
            and sequence[matched] == sequence[i + matched]
        ):
            matched += 1
        z[i] = matched
        if matched == 0:
            i += 1
            continue
        offset = 1
        while i + offset < n and offset + z[offset] < matched:
            z[i + offset] = z[offset]
            offset += 1
        i += offset
        matched -= offset
    return z


z_function = z_algorithm
Z_algorithm = z_algorithm
Z_algorism = z_algorithm
