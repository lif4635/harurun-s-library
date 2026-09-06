def langford(n, hooked=False):
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be nonnegative")
    if not isinstance(hooked, bool):
        raise TypeError("hooked must be a bool")
    if hooked:
        if n % 4 not in (1, 2):
            return None
        if n == 1:
            return [1, 0, 1]
        if n == 2:
            return [1, 2, 1, 0, 2]
        if n == 5:
            return [2, 3, 4, 2, 5, 3, 1, 4, 1, 0, 5]
        if n == 6:
            return [5, 6, 2, 3, 4, 2, 5, 3, 6, 4, 1, 0, 1]
        r = (n - 1) // 4
        if n % 4 == 1:
            blocks = (
                (2*r, 2*r+4, r-2),
                (r+2, 3*r+3, r),
                (6*r+1, 6*r+4, r-1),
                (5*r+2, 7*r+4, r-1),
                (2*r+3, 4*r+3, 1),
                (3*r+2, 7*r+3, 1),
                (2*r+1, 6*r+3, 1),
                (2*r+2, 6*r+2, 1),
            )
        else:
            blocks = (
                (2*r+2, 2*r+6, r-1),
                (r+2, 3*r+5, r-1),
                (3, 4*r+4, 1),
                (2*r+4, 4*r+5, 1),
                (r+3, 5*r+5, 1),
                (2*r+5, 6*r+5, 1),
                (2*r+3, 6*r+6, 1),
                (6*r+4, 6*r+7, r-1),
                (5*r+4, 7*r+6, r-1),
            )
        result = [0] * (2*n+1)
        for a, b, count in blocks:
            for j in range(count):
                result[a-j-3] = result[b+j-3] = b-a+2*j-1
        result[-3] = result[-1] = 1
        return result
    if n % 4 not in (0, 3):
        return None
    if n == 0:
        return []
    if n == 3:
        return [2, 3, 1, 2, 1, 3]
    if n == 4:
        return [2, 3, 4, 2, 1, 3, 1, 4]
    k = (n + 1) // 4
    result = list(range(4*k-4, 2*k-1, -2))
    result.append(4*k-2)
    result.extend(range(2*k-3, 0, -2))
    result.append(4*k-1)
    result.extend(range(1, 2*k-2, 2))
    result.extend(range(2*k, 4*k-3, 2))
    result.append(4*k if n % 4 == 0 else 2*k-1)
    result.extend(range(4*k-3, 2*k, -2))
    result.append(4*k-2)
    result.extend(range(2*k-2, 1, -2))
    result.extend((2*k-1, 4*k-1))
    result.extend(range(2, 2*k-1, 2))
    result.extend(range(2*k+1, 4*k-2, 2))
    if n % 4 == 0:
        result.extend((2*k-1, 4*k))
    return result
