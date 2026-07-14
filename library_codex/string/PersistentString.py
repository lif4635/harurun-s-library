_CHUNK_SIZE = 64
_MAX_SIZE = 1 << 60


class _Leaf:
    __slots__ = ("data", "size", "height")

    def __init__(self, data):
        self.data = data
        self.size = len(data)
        self.height = 0


class _Branch:
    __slots__ = ("left", "right", "size", "height")

    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.size = left.size + right.size
        height = left.height
        if right.height > height:
            height = right.height
        self.height = height + 1


def _make(left, right):
    if left is None:
        return right
    if right is None:
        return left
    if (
        isinstance(left, _Leaf)
        and isinstance(right, _Leaf)
        and left.size + right.size <= _CHUNK_SIZE
    ):
        return _Leaf(left.data + right.data)
    return _Branch(left, right)


def _balance(left, right):
    left_height = left.height
    right_height = right.height
    if left_height > right_height + 1:
        left_left = left.left
        left_right = left.right
        if left_left.height >= left_right.height:
            return _make(left_left, _make(left_right, right))
        middle_left = left_right.left
        middle_right = left_right.right
        return _make(
            _make(left_left, middle_left),
            _make(middle_right, right),
        )
    if right_height > left_height + 1:
        right_left = right.left
        right_right = right.right
        if right_right.height >= right_left.height:
            return _make(_make(left, right_left), right_right)
        middle_left = right_left.left
        middle_right = right_left.right
        return _make(
            _make(left, middle_left),
            _make(middle_right, right_right),
        )
    return _make(left, right)


def _join(left, right):
    if left is None:
        return right
    if right is None:
        return left
    path = []
    while True:
        if left.height > right.height + 1:
            path.append((0, left.left))
            left = left.right
        elif right.height > left.height + 1:
            path.append((1, right.right))
            right = right.left
        else:
            root = _make(left, right)
            break
    while path:
        side, fixed = path.pop()
        if side == 0:
            root = _balance(fixed, root)
        else:
            root = _balance(root, fixed)
    return root


def _split(root, index):
    if root is None:
        return None, None
    if index <= 0:
        return None, root
    if index >= root.size:
        return root, None
    path = []
    node = root
    position = index
    while isinstance(node, _Branch):
        left_size = node.left.size
        if position < left_size:
            path.append((0, node.right))
            node = node.left
        elif position > left_size:
            position -= left_size
            path.append((1, node.left))
            node = node.right
        else:
            left = node.left
            right = node.right
            break
    else:
        data = node.data
        left = _Leaf(data[:position]) if position else None
        right = _Leaf(data[position:]) if position < node.size else None
    while path:
        side, fixed = path.pop()
        if side == 0:
            right = _join(right, fixed)
        else:
            left = _join(fixed, left)
    return left, right


def _subroot(root, left, right):
    if root is None or left == right:
        return None
    if left == 0 and right == root.size:
        return root
    prefix, _ = _split(root, right)
    _, middle = _split(prefix, left)
    return middle


def _leaf_data(root):
    if root is None:
        return
    stack = [root]
    while stack:
        node = stack.pop()
        if isinstance(node, _Leaf):
            yield node.data
        else:
            stack.append(node.right)
            stack.append(node.left)


def _normalize(sequence):
    if isinstance(sequence, str):
        return sequence, 1
    if isinstance(sequence, (bytes, bytearray)):
        return bytes(sequence), 2
    return tuple(sequence), 0


def _construct(data):
    size = len(data)
    if size == 0:
        return None
    leaves = [
        _Leaf(data[left:left + _CHUNK_SIZE])
        for left in range(0, size, _CHUNK_SIZE)
    ]
    if len(leaves) == 1:
        return leaves[0]
    built = []
    stack = [(0, len(leaves), 0)]
    while stack:
        left, right, phase = stack.pop()
        if right - left == 1:
            built.append(leaves[left])
            continue
        if phase == 0:
            middle = (left + right) >> 1
            stack.append((left, right, 1))
            stack.append((middle, right, 0))
            stack.append((left, middle, 0))
        else:
            right_node = built.pop()
            left_node = built.pop()
            built.append(_make(left_node, right_node))
    return built[0]


class PersistentString:
    __slots__ = ("_root", "_kind")

    def __init__(self, sequence=""):
        data, self._kind = _normalize(sequence)
        if len(data) > _MAX_SIZE:
            raise OverflowError("persistent string is too long")
        self._root = _construct(data)

    @classmethod
    def _from_root(cls, root, kind):
        result = cls.__new__(cls)
        result._root = root
        result._kind = kind
        return result

    @staticmethod
    def MaxSize():
        return _MAX_SIZE

    def __len__(self):
        root = self._root
        return 0 if root is None else root.size

    def size(self):
        return len(self)

    def empty(self):
        return self._root is None

    @property
    def depth(self):
        root = self._root
        return 0 if root is None else root.height

    def copy(self):
        return self._from_root(self._root, self._kind)

    def _compatible(self, other):
        if not isinstance(other, PersistentString):
            other = PersistentString(other)
        if self._root is None:
            return other, other._kind
        if other._root is None:
            return other, self._kind
        if self._kind != other._kind:
            raise TypeError("persistent strings use different container types")
        return other, self._kind

    def __add__(self, other):
        other, kind = self._compatible(other)
        if len(self) > _MAX_SIZE - len(other):
            raise OverflowError("persistent string is too long")
        return self._from_root(_join(self._root, other._root), kind)

    def __iadd__(self, other):
        result = self + other
        self._root = result._root
        self._kind = result._kind
        return self

    def __mul__(self, count):
        if count < 0:
            raise ValueError("repeat count must be nonnegative")
        size = len(self)
        if count and size > _MAX_SIZE // count:
            raise OverflowError("persistent string is too long")
        result = self._from_root(None, self._kind)
        base = self.copy()
        repeat = count
        while repeat:
            if repeat & 1:
                result = result + base
            repeat >>= 1
            if repeat:
                base = base + base
        return result

    __rmul__ = __mul__

    def __imul__(self, count):
        result = self * count
        self._root = result._root
        return self

    def substr(self, position, length=None):
        size = len(self)
        if position < 0 or position > size:
            raise IndexError("substring position is out of range")
        if length is None:
            right = size
        else:
            if length < 0:
                raise ValueError("substring length must be nonnegative")
            right = position + length
            if right > size:
                right = size
        return self._from_root(
            _subroot(self._root, position, right), self._kind
        )

    def inserted(self, other, position):
        other, kind = self._compatible(other)
        size = len(self)
        if position < 0 or position > size:
            raise IndexError("insertion position is out of range")
        if size > _MAX_SIZE - len(other):
            raise OverflowError("persistent string is too long")
        left, right = _split(self._root, position)
        root = _join(_join(left, other._root), right)
        return self._from_root(root, kind)

    def insert(self, other, position):
        result = self.inserted(other, position)
        self._root = result._root
        self._kind = result._kind
        return self

    def deleted(self, left, right):
        size = len(self)
        if not (0 <= left <= right <= size):
            raise IndexError("deletion range is out of range")
        prefix, suffix = _split(self._root, right)
        before, _ = _split(prefix, left)
        return self._from_root(_join(before, suffix), self._kind)

    def replaced(self, left, right, other):
        if not (0 <= left <= right <= len(self)):
            raise IndexError("replacement range is out of range")
        return self.deleted(left, right).inserted(other, left)

    def __getitem__(self, index):
        size = len(self)
        if isinstance(index, slice):
            start, stop, step = index.indices(size)
            if step == 1:
                return self._from_root(
                    _subroot(self._root, start, stop), self._kind
                )
            return PersistentString(self.to_sequence()[index])
        if index < 0:
            index += size
        if index < 0 or index >= size:
            raise IndexError("persistent string index is out of range")
        node = self._root
        position = index
        while isinstance(node, _Branch):
            left_size = node.left.size
            if position < left_size:
                node = node.left
            else:
                position -= left_size
                node = node.right
        return node.data[position]

    def __iter__(self):
        for data in _leaf_data(self._root):
            yield from data

    def to_sequence(self):
        parts = list(_leaf_data(self._root))
        if self._kind == 1:
            return "".join(parts)
        if self._kind == 2:
            return b"".join(parts)
        result = []
        for part in parts:
            result.extend(part)
        return tuple(result)

    to_string = to_sequence

    def lcp(self, other):
        other, _ = self._compatible(other)
        if self._root is other._root:
            return len(self)
        first_parts = iter(_leaf_data(self._root))
        second_parts = iter(_leaf_data(other._root))
        first = next(first_parts, None)
        second = next(second_parts, None)
        first_index = 0
        second_index = 0
        result = 0
        while first is not None and second is not None:
            width = min(
                len(first) - first_index,
                len(second) - second_index,
            )
            first_slice = first[first_index:first_index + width]
            second_slice = second[second_index:second_index + width]
            if first_slice != second_slice:
                for offset in range(width):
                    if first_slice[offset] != second_slice[offset]:
                        return result + offset
            result += width
            first_index += width
            second_index += width
            if first_index == len(first):
                first = next(first_parts, None)
                first_index = 0
            if second_index == len(second):
                second = next(second_parts, None)
                second_index = 0
        return result

    def compare(self, other):
        other, _ = self._compatible(other)
        common = self.lcp(other)
        first_size = len(self)
        second_size = len(other)
        if common == first_size or common == second_size:
            return (first_size > second_size) - (first_size < second_size)
        return (self[common] > other[common]) - (self[common] < other[common])

    def __eq__(self, other):
        if not isinstance(other, PersistentString):
            try:
                other = PersistentString(other)
            except (TypeError, ValueError):
                return False
        if self._kind != other._kind:
            return False
        return len(self) == len(other) and self.lcp(other) == len(self)

    def __lt__(self, other):
        return self.compare(other) < 0

    def __le__(self, other):
        return self.compare(other) <= 0

    def __gt__(self, other):
        return self.compare(other) > 0

    def __ge__(self, other):
        return self.compare(other) >= 0

    def __str__(self):
        value = self.to_sequence()
        return value if self._kind == 1 else str(value)

    def __repr__(self):
        return f"PersistentString({self.to_sequence()!r})"
