def run_length_encode(s):
    encoded = []
    n = len(s)
    i = 0
    while i < n:
        current_char = s[i]
        count = 0
        while i < n and s[i] == current_char:
            count += 1
            i += 1
        encoded.append((current_char, count))
    return encoded
