from library_codex.convolution.FormalPowerSeries import DEFAULT_MOD


def number_of_increasing_sequences_between(lower, upper, mod=DEFAULT_MOD):
    """Count weakly increasing x with lower[i] <= x[i] < upper[i]."""
    if len(lower) != len(upper):
        raise ValueError("bound lengths differ")
    size = len(lower)
    if size == 0:
        return 1
    lower = list(lower)
    upper = list(upper)
    for index in range(1, size):
        if lower[index] < lower[index - 1]:
            lower[index] = lower[index - 1]
    for index in range(size - 2, -1, -1):
        if upper[index] > upper[index + 1]:
            upper[index] = upper[index + 1]
    for left, right in zip(lower, upper):
        if left >= right:
            return 0
    offset = lower[0]
    lower = [value - offset for value in lower]
    upper = [value - offset for value in upper]
    width = upper[-1]
    values = [0] * width
    for value in range(lower[0], upper[0]):
        values[value] = 1
    for index in range(1, size):
        running = 0
        left = lower[index]
        right = upper[index]
        for value in range(width):
            running += values[value]
            if running >= mod:
                running -= mod
            values[value] = running if left <= value < right else 0
    return sum(values) % mod


NumberofIncreasingSequencesBetweenTwoSequences = (
    number_of_increasing_sequences_between
)
