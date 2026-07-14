def manacher(sequence):
    n = len(sequence)
    radius = [0] * n
    center = 0
    current = 0
    while center < n:
        while (
            center - current >= 0
            and center + current < n
            and sequence[center - current] == sequence[center + current]
        ):
            current += 1
        radius[center] = current
        offset = 1
        while (
            center - offset >= 0
            and center + offset < n
            and offset + radius[center - offset] < current
        ):
            radius[center + offset] = radius[center - offset]
            offset += 1
        center += offset
        current -= offset
    return radius


manacher_odd = manacher


def manacher_even(sequence):
    n = len(sequence)
    radius = [0] * n
    left = 0
    right = -1
    for center in range(n):
        if center > right:
            current = 0
        else:
            mirror = left + right - center + 1
            current = radius[mirror]
            bound = right - center + 1
            if current > bound:
                current = bound
        while (
            center - current - 1 >= 0
            and center + current < n
            and sequence[center - current - 1] == sequence[center + current]
        ):
            current += 1
        radius[center] = current
        if center + current - 1 > right:
            left = center - current
            right = center + current - 1
    return radius


def palindrome_radii(sequence):
    return manacher(sequence), manacher_even(sequence)


def enumerate_palindrome_lengths(sequence):
    n = len(sequence)
    if n == 0:
        return []
    odd, even = palindrome_radii(sequence)
    result = [0] * (2 * n - 1)
    for center in range(n):
        result[center << 1] = (odd[center] << 1) - 1
        if center:
            result[(center << 1) - 1] = even[center] << 1
    return result


def enumerate_palindromes(sequence, include_empty=True):
    n = len(sequence)
    if n == 0:
        return []
    odd, even = palindrome_radii(sequence)
    result = [None] * (2 * n - 1)
    for center in range(n):
        radius = odd[center]
        result[center << 1] = (
            center - radius + 1,
            center + radius,
        )
        if center:
            radius = even[center]
            position = (center << 1) - 1
            if radius or include_empty:
                result[position] = (center - radius, center + radius)
            else:
                result[position] = (-1, -1)
    return result


def get_palindromes(sequence):
    return enumerate_palindromes(sequence, False)


def enumerate_leftmost_palindromes(sequence):
    n = len(sequence)
    if n == 0:
        return []
    longest = [1] * n
    for left, right in enumerate_palindromes(sequence):
        if right > left:
            length = right - left
            if length > longest[right - 1]:
                longest[right - 1] = length
    for end in range(n - 2, -1, -1):
        inherited = longest[end + 1] - 2
        if inherited > longest[end]:
            longest[end] = inherited
    return [end + 1 - longest[end] for end in range(n)]


Manacher = enumerate_palindrome_lengths
