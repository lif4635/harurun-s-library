def run_length_encode(sequence):
    iterator = iter(sequence)
    try:
        value = next(iterator)
    except StopIteration:
        return []
    result = []
    count = 1
    for current in iterator:
        if current == value:
            count += 1
        else:
            result.append((value, count))
            value = current
            count = 1
    result.append((value, count))
    return result


def run_length_decode(encoded, container_type=list):
    result = []
    for value, count in encoded:
        if count < 0:
            raise ValueError("run length must be nonnegative")
        result.extend([value] * count)
    if container_type is str:
        return "".join(result)
    if container_type is bytes:
        return bytes(result)
    if container_type is bytearray:
        return bytearray(result)
    if container_type is tuple:
        return tuple(result)
    return result if container_type is list else container_type(result)


RunLengthEncoding = run_length_encode
rle = run_length_encode
