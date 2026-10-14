"""素数法の正方行列の余因子行列を、特異な場合も含めて求める。"""

def adjugate(matrix, mod=998244353):
    """余因子を転置したN×Nの行列を返す。O(N^3)、入力は変更しない。"""
    n = len(matrix)
    if mod < 2:
        raise ValueError('mod must be prime')
    if any((len(row) != n for row in matrix)):
        raise ValueError('matrix must be square')
    if not n:
        return []
    if n == 1:
        return [[1]]
    rows = [[x % mod for x in row] + [int(i == j) for j in range(n)] for (i, row) in enumerate(matrix)]
    rank = 0
    factor = 1
    free = -1
    pivots = []
    width = n * 2
    for column in range(n):
        pivot = rank
        while pivot < n and rows[pivot][column] == 0:
            pivot += 1
        if pivot == n:
            if free >= 0:
                return [[0] * n for _ in range(n)]
            free = column
            continue
        if pivot != rank:
            (rows[pivot], rows[rank]) = (rows[rank], rows[pivot])
            factor = -factor
        source = rows[rank]
        value = source[column]
        factor = factor * value % mod
        inverse = pow(value, -1, mod)
        source[column] = 1
        for j in range(column + 1, width):
            source[j] = source[j] * inverse % mod
        for i in range(n):
            if i == rank:
                continue
            target = rows[i]
            coefficient = target[column]
            if coefficient:
                target[column] = 0
                for j in range(column + 1, width):
                    target[j] = (target[j] - coefficient * source[j]) % mod
        pivots.append(column)
        rank += 1
    if rank == n:
        return [[x * factor % mod for x in row[n:]] for row in rows]
    if n - 1 - free & 1:
        factor = -factor
    left = [x * factor % mod for x in rows[-1][n:]]
    result = [[0] * n for _ in range(n)]
    result[free] = left
    for (i, column) in enumerate(pivots):
        coefficient = -rows[i][free] % mod
        result[column] = [coefficient * x % mod for x in left]
    return result
import sys

def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    matrix = [list(map(int, read().split())) for _ in range(n)]
    result = adjugate(matrix)
    sys.stdout.write('\n'.join((' '.join(map(str, row)) for row in result)) + '\n')
if __name__ == '__main__':
    main()
