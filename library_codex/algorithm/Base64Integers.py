_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/."
_DECODE = {character: index for index, character in enumerate(_ALPHABET)}


def encode_integers(values, signed_bits=64):
    values = list(values)
    if not values:
        return ""
    if any(value < 0 for value in values):
        width = signed_bits
        encoded_values = [value & ((1 << width) - 1) for value in values]
    else:
        width = max(6, max(values).bit_length())
        encoded_values = values
    chunks = [width]
    accumulator = 0
    accumulator_bits = 0
    for value in encoded_values:
        accumulator |= value << accumulator_bits
        accumulator_bits += width
        while accumulator_bits >= 6:
            chunks.append(accumulator & 63)
            accumulator >>= 6
            accumulator_bits -= 6
    if accumulator_bits:
        chunks.append(accumulator & 63)
    return "".join(_ALPHABET[value] for value in chunks)


def decode_integers(encoded, signed=False):
    if not encoded:
        return []
    try:
        chunks = [_DECODE[character] for character in encoded]
    except KeyError as error:
        raise ValueError("invalid base64 integer character") from error
    width = chunks[0]
    if width == 0:
        raise ValueError("invalid encoded bit width")
    count = (len(chunks) - 1) * 6 // width
    accumulator = 0
    bits = 0
    result = []
    source = 1
    for _ in range(count):
        while bits < width:
            accumulator |= chunks[source] << bits
            bits += 6
            source += 1
        value = accumulator & ((1 << width) - 1)
        accumulator >>= width
        bits -= width
        if signed and value >> (width - 1):
            value -= 1 << width
        result.append(value)
    return result


encode = encode_integers
decode = decode_integers
