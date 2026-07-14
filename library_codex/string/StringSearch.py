from library_codex.string.SuffixArray import SuffixArray


def lcp_naive(first, second):
    limit = min(len(first), len(second))
    index = 0
    while index < limit and first[index] == second[index]:
        index += 1
    return index


class StringSearch:
    __slots__ = (
        "sequence", "S", "n", "N", "index", "sa", "la", "invsa",
    )

    def __init__(self, sequence, upper=None):
        self.sequence = sequence
        self.S = sequence
        self.n = len(sequence)
        self.N = self.n
        self.index = SuffixArray(sequence, upper)
        self.sa = self.index.sa
        self.la = self.index.lcp
        self.invsa = self.index.rank

    def lcp(self, *arguments):
        if len(arguments) == 2:
            first, second = arguments
            if isinstance(first, tuple) and isinstance(second, tuple):
                return self.index.lcp_substring(
                    first[0], first[1], second[0], second[1]
                )
            return self.index.lcp_suffix(first, second)
        if len(arguments) == 4:
            return self.index.lcp_substring(*arguments)
        raise TypeError("lcp expects two suffix indices or two substring ranges")

    def strcmp(self, *arguments):
        if len(arguments) == 2:
            first, second = arguments
            if isinstance(first, tuple) and isinstance(second, tuple):
                return self.index.compare_substring(
                    first[0], first[1], second[0], second[1]
                )
            return self.index.compare_suffix(first, second)
        if len(arguments) == 4:
            return self.index.compare_substring(*arguments)
        raise TypeError(
            "strcmp expects two suffix indices or two substring ranges"
        )

    compare = strcmp

    def search(self, pattern):
        return self.index.search(pattern)

    find_range = search

    def count(self, pattern):
        return self.index.count(pattern)

    def occurrences(self, pattern, sort_positions=False):
        return self.index.occurrences(pattern, sort_positions)
