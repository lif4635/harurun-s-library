CASES = {
    "union_find/UnionFind": '''
def solve(n):
    uf = UnionFind(n)
    for i in range(1, n):
        uf.merge(i, (i * 12347) % i)
    print(uf.size(0), uf.component_count, uf.same(0, n-1), len(uf.groups()[0]))
    print(uf.find(0), uf.leader(0), uf.root(0), uf.unite(0, 0), uf.union(0, 0))
    print(str(UnionFind(3)))
solve(int(sys.stdin.readline()))
''',
    "fenwick_tree/BIT": '''
def solve(n):
    values = [(i * 12347) % 100003 for i in range(n)]
    bit = BIT(values)
    empty = BIT(0)
    print(empty.sum(0), empty.lower_bound(1))
    checksum = 0
    for i in range(n):
        bit.add(i, i % 97)
        checksum += bit.sum(i, min(n, i + 127))
    bit.set(0, 7)
    print(checksum, bit.sum(n), bit.get(0), len(bit), bit.tolist()[-1])
    print(bit.lower_bound(1), bit.lower_bound(bit.sum(n)), bit.lower_bound(bit.sum(n) + 1))
solve(int(sys.stdin.readline()))
''',
    "segment_tree/SegTree": '''
def solve(n):
    values = [(i * 12347) % 100003 for i in range(n)]
    tree = SegTree(lambda a, b: a + b, 0, values)
    checksum = 0
    for i in range(n):
        tree.add(i, i % 97)
        checksum += tree.prod(i, min(n, i + 127))
    tree.set(0, 7)
    print(checksum, tree.all_prod(), tree.get(0), tree.tolist()[-1], tree.query(0, n))
    print(tree.max_right(0, lambda x: x < 100000), tree.min_left(n, lambda x: x < 100000))
    print(SegTree(lambda a, b: a + b, 0, 0).prod(0, 0))
    strings = SegTree(lambda a, b: a + b, '', ['a', 'b', 'c'])
    strings.add(1, 'z')
    print(strings.prod(0, 3), strings.prod(1, 3))
    pairs = SegTree(lambda a, b: (a[0]+b[0], a[1]+b[1]), (0,0), [(1,2), (3,4)])
    print(pairs.prod(0, 2))
solve(int(sys.stdin.readline()))
''',
    "convolution/NTT998": '''
def checksum(values):
    answer = 0
    for i, value in enumerate(values):
        answer = (answer + (i + 1) * value) % MOD
    return answer
def solve(n):
    for size in [1, 8, 59, 60, 61, 64, 65, 129, n]:
        a = [MOD - 1] * size
        result = multiply(a, a)
        expected = [min(i + 1, 2 * size - 1 - i, size) for i in range(2 * size - 1)]
        assert result == expected
        assert square(a) == expected
    a = [(i * 12347 - 45678) for i in range(n)]
    b = [(i * 34567 - 67890) for i in range(n + 1)]
    print(checksum(multiply(a, b)), checksum(square(a)))
    print(multiply([], [1]), multiply([-1], [2]), square([-3]))
    v = [i % MOD for i in range(128)]
    old = v[:]
    ntt(v)
    intt(v)
    assert old == v
solve(int(sys.stdin.readline()))
''',
    "fps998/FPS": '''
def checksum(values):
    answer = 0
    for i, value in enumerate(values):
        answer = (answer + (i + 1) * value) % MOD
    return answer
def solve(n):
    a = [1] + [(i * 12347) % MOD for i in range(1, n)]
    b = [0] + a[1:]
    inverse = fps_inv(a)
    assert multiply(a, inverse)[:n] == [1] + [0] * (n-1)
    logarithm = fps_log(a)
    exponential = fps_exp(b)
    assert fps_log(exponential) == b
    print(checksum(inverse), checksum(logarithm), checksum(exponential))
    print(checksum(fps_div(b, a)), checksum(fps_pow(a, 7)), checksum(fps_pow(a, -3)))
    print(checksum(taylor_shift(a, -7)), checksum(fps_product([[1,2], [3,4], [5,6]])))
    print(fps_sqrt([1, 2, 1], 12))
    print(fps_integral(fps_diff([1,2,3])), fps_eval([-2,3], -7))
    print(shrink([1,0,0]), fps_add([1,2], [-1]), fps_sub([1], [2,3]), fps_neg([1,2]))
    print(fps_inv([1, 1], 8), fps_exp([0, 1], 8), fps_pow([0,1,2], 3, 8))
    root = fps_sqrt(multiply(a, a)[:n], n)
    assert root is not None
    assert multiply(root, root)[:n] == multiply(a, a)[:n]
    print(checksum(root), fps_sqrt([0,1]), fps_sqrt([3]))
    print(fps_product([[1], [2,3], [4,5,6]]), fps_product([]))
    print(fps_inv([], 0), fps_log([], 0), fps_exp([], 4), fps_pow([], 0, 4))
solve(int(sys.stdin.readline()))
''',
}

REGRESSIONS = {
    "union_find/UnionFind": '''
for size in range(1, 19):
    uf = UnionFind(size)
    for step in range(size * 5):
        a = (step * 13 + 7) % size
        b = (step * step * 11 + 3) % size
        uf.merge(a, b)
        print(uf.same(a, b), uf.size(a), uf.component_count)
    print(uf.groups(), str(uf), repr(uf))
''',
    "fenwick_tree/BIT": '''
for size in range(1, 19):
    bit = BIT(size)
    expected = [0] * size
    for step in range(size * 5):
        i = (step * 13 + 7) % size
        value = step * 17 % 97
        bit.set(i, value)
        expected[i] = value
        assert bit.tolist() == expected
        print(bit.sum(i), bit.sum(i, size), bit.lower_bound(value))
    print(str(bit), repr(bit))
''',
    "segment_tree/SegTree": '''
for size in range(1, 19):
    tree = SegTree(lambda a, b: a + b, 0, size)
    expected = [0] * size
    for step in range(size * 5):
        i = (step * 13 + 7) % size
        value = step * 17 % 97
        tree.set(i, value)
        expected[i] = value
        assert tree.tolist() == expected
        print(tree.prod(i, size), tree.max_right(i, lambda v: v <= 100), tree.min_left(i, lambda v: v <= 100))
    print(str(tree), repr(tree))
''',
    "convolution/NTT998": '''
for size in range(1, 82):
    first = [(i * i * 99337 + size * 5437) % MOD - MOD // 2 for i in range(size)]
    second = [(i * 19471 - size * 937) % MOD for i in range(83-size)]
    result = multiply(first, second)
    expected = [0] * 82
    for i in range(len(first)):
        for j in range(len(second)):
            expected[i+j] = (expected[i+j] + first[i] * second[j]) % MOD
    assert result == expected
    print(result)
print(multiply([9223372036854775807], [-9223372036854775807]), square([-9223372036854775807]))
''',
    "fps998/FPS": '''
for size in range(1, 40):
    a = [1] + [(i * i * 99337 + size * 5437) % MOD for i in range(1,size)]
    print(fps_inv(a), fps_log(a), fps_pow(a, -2), fps_div([1], a, size))
    print(fps_exp([0] + a[1:]), taylor_shift(a, -37))
    print(fps_sqrt(multiply(a, a), size), fps_product([a, [1,2,3]]))
''',
}
