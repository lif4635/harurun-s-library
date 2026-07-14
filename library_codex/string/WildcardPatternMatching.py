from library_codex.convolution.NTT import get_ntt


_WILDCARD_MODS = (998244353, 924844033, 1012924417)


def _encode_sequences(text, pattern, wildcard):
    mapping = {}
    next_id = 1
    try:
        encoded_text = []
        for value in text:
            if value == wildcard:
                encoded_text.append(0)
            else:
                identifier = mapping.get(value)
                if identifier is None:
                    identifier = next_id
                    next_id += 1
                    mapping[value] = identifier
                encoded_text.append(identifier)
        encoded_pattern = []
        for value in pattern:
            if value == wildcard:
                encoded_pattern.append(0)
            else:
                identifier = mapping.get(value)
                if identifier is None:
                    identifier = next_id
                    next_id += 1
                    mapping[value] = identifier
                encoded_pattern.append(identifier)
        return encoded_text, encoded_pattern, next_id - 1
    except TypeError:
        symbols = []

        def encode(sequence):
            result = []
            for value in sequence:
                if value == wildcard:
                    result.append(0)
                    continue
                for index, symbol in enumerate(symbols):
                    if value == symbol:
                        result.append(index + 1)
                        break
                else:
                    symbols.append(value)
                    result.append(len(symbols))
            return result

        encoded_text = encode(text)
        encoded_pattern = encode(pattern)
        return encoded_text, encoded_pattern, len(symbols)


def _brute(text, pattern, wildcard):
    text_size = len(text)
    pattern_size = len(pattern)
    result = [1] * (text_size - pattern_size + 1)
    for start in range(len(result)):
        for index in range(pattern_size):
            left = text[start + index]
            right = pattern[index]
            if left != wildcard and right != wildcard and left != right:
                result[start] = 0
                break
    return result


def _matching_mod(text, pattern, mod):
    text_size = len(text)
    pattern_size = len(pattern)
    output_size = text_size + pattern_size - 1
    size = 1 << (output_size - 1).bit_length()
    transform = get_ntt(mod)
    transform._check_length(size)
    accumulated = [0] * size

    for component in range(3):
        if component == 0:
            left = [value * value % mod if value else 0 for value in text]
            right = [1 if value else 0 for value in reversed(pattern)]
        elif component == 1:
            left = [(-2 * value) % mod if value else 0 for value in text]
            right = [value for value in reversed(pattern)]
        else:
            left = [1 if value else 0 for value in text]
            right = [
                value * value % mod if value else 0
                for value in reversed(pattern)
            ]
        left.extend([0] * (size - text_size))
        right.extend([0] * (size - pattern_size))
        transform.butterfly(left)
        transform.butterfly(right)
        for index in range(size):
            accumulated[index] = (
                accumulated[index] + left[index] * right[index]
            ) % mod

    transform.butterfly_inv(accumulated)
    offset = pattern_size - 1
    return [
        accumulated[offset + start] == 0
        for start in range(text_size - pattern_size + 1)
    ]


def wildcard_pattern_matching(text, pattern, wildcard=0):
    text_size = len(text)
    pattern_size = len(pattern)
    if pattern_size == 0:
        return [1] * (text_size + 1)
    if text_size < pattern_size:
        return []
    if pattern_size <= 64 or (
        text_size - pattern_size + 1
    ) * pattern_size <= 200000:
        return _brute(text, pattern, wildcard)

    encoded_text, encoded_pattern, symbol_count = _encode_sequences(
        text, pattern, wildcard
    )
    maximum_difference = max(0, symbol_count - 1)
    bound = pattern_size * maximum_difference * maximum_difference
    result = None
    product = 1
    for mod in _WILDCARD_MODS:
        current = _matching_mod(encoded_text, encoded_pattern, mod)
        if result is None:
            result = current
        else:
            for index in range(len(result)):
                result[index] = result[index] and current[index]
        product *= mod
        if bound < product:
            break
    return [int(value) for value in result]


def wildcard_match_positions(text, pattern, wildcard=0):
    return [
        index
        for index, matched in enumerate(
            wildcard_pattern_matching(text, pattern, wildcard)
        )
        if matched
    ]


wildcard_matching = wildcard_pattern_matching
