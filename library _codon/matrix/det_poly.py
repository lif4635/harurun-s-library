MOD = 998244353

def hessenberg_reduction(m):
    N = len(m)
    for r in range(N - 2):
        piv = -1
        for h in range(r + 1, N):
            if m[h][r] != 0:
                piv = h
                break
        if piv < 0:
            continue
        m[r + 1], m[piv] = m[piv], m[r + 1]
        for row in m:
            row[r + 1], row[piv] = row[piv], row[r + 1]
        rinv = pow(m[r + 1][r], MOD-2, MOD)
        for i in range(r + 2, N):
            n = (m[i][r] * rinv) % MOD
            for j in range(N):
                m[i][j] = (m[i][j] - m[r + 1][j] * n) % MOD
                m[j][r + 1] = (m[j][r + 1] + m[j][i] * n) % MOD
    return m

def characteristic_poly(m):
    m = hessenberg_reduction(m)
    N = len(m)
    p = [[1]]
    for i in range(N):
        p.append([0] * (i + 2))
        for j in range(i + 1):
            p[i + 1][j + 1] = (p[i + 1][j + 1] + p[i][j]) % MOD
        for j in range(i + 1):
            p[i + 1][j] = (p[i + 1][j] - p[i][j] * m[i][i]) % MOD
        betas = 1
        for j in range(i - 1, -1, -1):
            betas = (betas * m[j + 1][j]) % MOD
            hb = (-m[j][i] * betas) % MOD
            for k in range(j + 1):
                p[i + 1][k] = (p[i + 1][k] + hb * p[j][k]) % MOD
    return p[N]

def det_poly(m0, m1):
    N = len(m0)
    mul_x = 0
    dat_inv = 1
    p = 0
    while p < N:
        pivot = next((row for row in range(p, N) if m1[row][p] != 0), -1)
        if pivot < 0:
            mul_x += 1
            if mul_x > N:
                return [0] * (N + 1)
            for row in range(p):
                v = m1[row][p]
                m1[row][p] = 0
                for i in range(N):
                    m0[i][p] = (m0[i][p] - v * m0[i][row]) % MOD
            for i in range(N):
                m0[i][p], m1[i][p] = m1[i][p], m0[i][p]
            continue
        if pivot != p:
            m1[p], m1[pivot] = m1[pivot], m1[p]
            m0[p], m0[pivot] = m0[pivot], m0[p]
            dat_inv = (-dat_inv) % MOD
        v = m1[p][p]
        vinv = pow(v, MOD - 2, MOD)
        dat_inv = (dat_inv * v) % MOD
        for col in range(N):
            m0[p][col] = (m0[p][col] * vinv) % MOD
            m1[p][col] = (m1[p][col] * vinv) % MOD
        for row in range(N):
            if row == p:
                continue
            v = m1[row][p]
            for col in range(N):
                m0[row][col] = (m0[row][col] - m0[p][col] * v) % MOD
                m1[row][col] = (m1[row][col] - m1[p][col] * v) % MOD
        p += 1
    for vec in m0:
        for i in range(len(vec)):
            vec[i] = (-vec[i]) % MOD
    poly = characteristic_poly(m0)
    poly = [(x * dat_inv) % MOD for x in poly]
    poly = poly[mul_x:]
    poly += [0] * (N + 1 - len(poly))
    return poly