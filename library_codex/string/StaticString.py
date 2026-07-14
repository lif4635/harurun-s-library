from bisect import bisect_right

from library_codex.string.StringSearch import lcp_naive
from library_codex.string.SuffixArray import SuffixArray, suffix_array


def _normalize(sequence):
    if isinstance(sequence, str):
        return sequence, 1
    if isinstance(sequence, (bytes, bytearray)):
        return bytes(sequence), 2
    return tuple(sequence), 0


def _pack(kind, parts):
    if kind == 1:
        return "".join(parts)
    if kind == 2:
        return b"".join(parts)
    result = []
    for part in parts:
        result.extend(part)
    return tuple(result)


class StaticStringBase:
    __slots__ = (
        "sequence", "S", "size", "index", "SA", "RSA", "LCP", "_kind",
    )

    def __init__(self, sequence):
        sequence, self._kind = _normalize(sequence)
        self.sequence = sequence
        self.S = sequence
        self.size = len(sequence)
        self.index = SuffixArray(sequence)
        self.SA = self.index.sa
        self.RSA = self.index.rank
        self.LCP = self.index.lcp

    def view(self, left=0, right=None):
        if right is None:
            right = self.size
        return StaticString(self, left, right)

    def suffix_lowerbound(self, pattern):
        return self.index.search(pattern)[0]

    def suffix_upperbound(self, pattern):
        return self.index.search(pattern)[1]

    def count(self, pattern):
        return self.index.count(pattern)

    def occurrences(self, pattern, sort_positions=False):
        return self.index.occurrences(pattern, sort_positions)


class StaticString:
    __slots__ = ("base", "left", "right", "l", "r")

    def __init__(self, base, left=0, right=None):
        if right is None:
            right = base.size
        if not (0 <= left <= right <= base.size):
            raise IndexError("static string range is out of range")
        self.base = base
        self.left = self.l = left
        self.right = self.r = right

    @classmethod
    def from_sequence(cls, sequence):
        return StaticStringBase(sequence).view()

    from_string = from_sequence

    def __len__(self):
        return self.right - self.left

    def __getitem__(self, index):
        size = len(self)
        if isinstance(index, tuple):
            parts = []
            for item in index:
                if isinstance(item, slice):
                    part = self[item]
                else:
                    position = item + size if item < 0 else item
                    if position < 0 or position >= size:
                        raise IndexError("static string index is out of range")
                    part = StaticString(
                        self.base,
                        self.left + position,
                        self.left + position + 1,
                    )
                if isinstance(part, StaticString):
                    parts.append(part)
                else:
                    parts.append(StaticString.from_sequence(part))
            return MergedStaticString(parts)
        if isinstance(index, slice):
            start, stop, step = index.indices(size)
            if step == 1:
                return StaticString(
                    self.base, self.left + start, self.left + stop
                )
            return StaticString.from_sequence(self.materialize()[index])
        if index < 0:
            index += size
        if index < 0 or index >= size:
            raise IndexError("static string index is out of range")
        return self.base.sequence[self.left + index]

    def materialize(self):
        return self.base.sequence[self.left:self.right]

    to_sequence = materialize

    def lcp(self, other):
        if isinstance(other, MergedStaticString):
            return MergedStaticString((self,)).lcp(other)
        limit = min(len(self), len(other))
        if limit == 0:
            return 0
        if self.base is other.base:
            return self.base.index.lcp_substring(
                self.left, self.right, other.left, other.right
            )
        return lcp_naive(self, other)

    def compare(self, other):
        if isinstance(other, MergedStaticString):
            return -other.compare(self)
        common = self.lcp(other)
        first_size = len(self)
        second_size = len(other)
        if common == first_size or common == second_size:
            return (first_size > second_size) - (first_size < second_size)
        return (self[common] > other[common]) - (self[common] < other[common])

    cmp = compare

    def startswith(self, prefix):
        return len(prefix) <= len(self) and self.lcp(prefix) == len(prefix)

    startsWith = startswith

    def suffix_array(self):
        return [
            StaticString(self.base, self.left + offset, self.right)
            for offset in suffix_array(self.materialize())
        ]

    def __add__(self, other):
        return MergedStaticString((self, other))

    def __eq__(self, other):
        return (
            isinstance(other, (StaticString, MergedStaticString))
            and len(self) == len(other)
            and self.lcp(other) == len(self)
        )

    def __lt__(self, other):
        return self.compare(other) < 0

    def __le__(self, other):
        return self.compare(other) <= 0

    def __gt__(self, other):
        return self.compare(other) > 0

    def __ge__(self, other):
        return self.compare(other) >= 0

    def __str__(self):
        value = self.materialize()
        return value if self.base._kind == 1 else str(value)

    def __repr__(self):
        return f"StaticString({self.materialize()!r})"


class MergedStaticString:
    __slots__ = ("parts", "lencum", "_kind")

    def __init__(self, parts=()):
        self.parts = []
        self.lencum = []
        self._kind = -1
        for part in parts:
            self._append(part)

    @property
    def S(self):
        return self.parts

    def _append(self, value):
        pending = [value]
        while pending:
            current = pending.pop()
            if isinstance(current, MergedStaticString):
                pending.extend(reversed(current.parts))
                continue
            if not isinstance(current, StaticString):
                current = StaticString.from_sequence(current)
            kind = current.base._kind
            if self._kind == -1:
                self._kind = kind
            elif self._kind != kind:
                raise TypeError(
                    "merged strings use different container types"
                )
            if len(current) == 0:
                continue
            if (
                self.parts
                and self.parts[-1].base is current.base
                and self.parts[-1].right == current.left
            ):
                previous = self.parts[-1]
                self.parts[-1] = StaticString(
                    previous.base, previous.left, current.right
                )
                self.lencum[-1] += len(current)
            else:
                self.parts.append(current)
                total = self.lencum[-1] if self.lencum else 0
                self.lencum.append(total + len(current))

    def __len__(self):
        return 0 if not self.lencum else self.lencum[-1]

    def __iadd__(self, other):
        self._append(other)
        return self

    def __add__(self, other):
        result = MergedStaticString(self.parts)
        result += other
        return result

    def __getitem__(self, index):
        size = len(self)
        if isinstance(index, slice):
            start, stop, step = index.indices(size)
            if step != 1:
                return MergedStaticString((
                    StaticString.from_sequence(self.materialize()[index]),
                ))
            if start == stop:
                result = MergedStaticString()
                result._kind = self._kind
                return result
            part_index = bisect_right(self.lencum, start)
            result = MergedStaticString()
            offset = self.lencum[part_index - 1] if part_index else 0
            while part_index < len(self.parts) and offset < stop:
                part = self.parts[part_index]
                part_right = self.lencum[part_index]
                local_left = start - offset if start > offset else 0
                local_right = stop - offset if stop < part_right else len(part)
                result += part[local_left:local_right]
                offset = part_right
                part_index += 1
            return result
        if index < 0:
            index += size
        if index < 0 or index >= size:
            raise IndexError("merged string index is out of range")
        part_index = bisect_right(self.lencum, index)
        offset = self.lencum[part_index - 1] if part_index else 0
        return self.parts[part_index][index - offset]

    def materialize(self):
        if not self.parts:
            return "" if self._kind in (-1, 1) else (b"" if self._kind == 2 else ())
        return _pack(
            self._kind, [part.materialize() for part in self.parts]
        )

    to_sequence = materialize

    def lcp(self, other):
        if isinstance(other, StaticString):
            other = MergedStaticString((other,))
        if not isinstance(other, MergedStaticString):
            other = MergedStaticString((other,))
        if self is other:
            return len(self)
        if not self.parts or not other.parts:
            return 0
        if self._kind != other._kind:
            raise TypeError("merged strings use different container types")
        first_part = 0
        second_part = 0
        first_offset = 0
        second_offset = 0
        result = 0
        while (
            first_part < len(self.parts)
            and second_part < len(other.parts)
        ):
            first = self.parts[first_part]
            second = other.parts[second_part]
            first_view = StaticString(
                first.base, first.left + first_offset, first.right
            )
            second_view = StaticString(
                second.base, second.left + second_offset, second.right
            )
            width = min(len(first_view), len(second_view))
            common = first_view.lcp(second_view)
            if common < width:
                return result + common
            result += width
            first_offset += width
            second_offset += width
            if first_offset == len(first):
                first_part += 1
                first_offset = 0
            if second_offset == len(second):
                second_part += 1
                second_offset = 0
        return result

    def compare(self, other):
        if isinstance(other, StaticString):
            other = MergedStaticString((other,))
        elif not isinstance(other, MergedStaticString):
            other = MergedStaticString((other,))
        common = self.lcp(other)
        first_size = len(self)
        second_size = len(other)
        if common == first_size or common == second_size:
            return (first_size > second_size) - (first_size < second_size)
        return (self[common] > other[common]) - (self[common] < other[common])

    cmp = compare

    def startswith(self, prefix):
        return len(prefix) <= len(self) and self.lcp(prefix) == len(prefix)

    startsWith = startswith

    def __eq__(self, other):
        return (
            isinstance(other, (StaticString, MergedStaticString))
            and len(self) == len(other)
            and self.lcp(other) == len(self)
        )

    def __lt__(self, other):
        return self.compare(other) < 0

    def __le__(self, other):
        return self.compare(other) <= 0

    def __gt__(self, other):
        return self.compare(other) > 0

    def __ge__(self, other):
        return self.compare(other) >= 0

    def __str__(self):
        value = self.materialize()
        return value if self._kind in (-1, 1) else str(value)

    def __repr__(self):
        return f"MergedStaticString({self.materialize()!r})"


def to_static_string(sequence):
    return StaticString.from_sequence(sequence)


toStaticString = to_static_string


def to_static_strings(sequences):
    sequences = list(sequences)
    if not sequences:
        return []
    normalized = []
    kind = None
    for sequence in sequences:
        data, current_kind = _normalize(sequence)
        if kind is None:
            kind = current_kind
        elif kind != current_kind:
            raise TypeError("static strings use different container types")
        normalized.append(data)
    combined = _pack(kind, normalized)
    base = StaticStringBase(combined)
    result = []
    offset = 0
    for sequence in normalized:
        right = offset + len(sequence)
        result.append(StaticString(base, offset, right))
        offset = right
    return result


toStaticStrings = to_static_strings


def init_suffix_array(value):
    if isinstance(value, StaticStringBase):
        return [
            StaticString(value, offset, value.size) for offset in value.SA
        ]
    return value.suffix_array()


initSuffixArray = init_suffix_array
