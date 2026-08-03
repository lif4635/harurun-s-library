"""Enumeration of additive integer partitions."""


def integer_partitions(number):
    """Return all partitions in nonincreasing order, without recursion."""
    if number < 0:
        raise ValueError("number must be nonnegative")
    if number == 0:
        return [()]
    result = []
    partition = [number]
    while True:
        result.append(tuple(partition))
        remainder = 0
        while partition and partition[-1] == 1:
            remainder += partition.pop()
        if not partition:
            break
        partition[-1] -= 1
        remainder += 1
        while remainder > partition[-1]:
            remainder -= partition[-1]
            partition.append(partition[-1])
        partition.append(remainder)
    return result


def integer_partitions_up_to(limit):
    """Return partitions for each integer from 0 through limit."""
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    return [integer_partitions(number) for number in range(limit + 1)]
