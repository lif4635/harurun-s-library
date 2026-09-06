from library_codex.combinatorics.Langford import langford


def skolem(n, hooked=False):
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be nonnegative")
    if not isinstance(hooked, bool):
        raise TypeError("hooked must be a bool")
    if n == 0:
        return None if hooked else []
    result = langford(n - 1, hooked)
    if result is None:
        return None
    return [1, 1] + [value + 1 if value else 0 for value in result]
