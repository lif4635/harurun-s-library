def hungarian(table):
    """最小重み最大マッチング"""
    n = len(table)+1
    m = len(table[0])+1
    
    #i-indexに直す
    a = [[table[i-1][j-1] if i*j != 0 else 0 for j in range(m)] for i in range(n)]
    
    assert n <= m
    p = [0]*m
    way = [0]*m
    u = [0]*n
    v = [0]*m
    
    for i in range(1,n):
        p[0] = i
        minV = [inf]*m
        used = [False]*m
        j0 = 0
        
        while p[j0] != 0:
            i0 = p[j0]
            used[j0] = True
            delta = inf
            for j in range(1,m):
                if used[j]: continue
                curr = a[i0][j] - u[i0] - v[j]
                if curr < minV[j]:
                    minV[j] = curr
                    way[j] = j0
                if minV[j] < delta:
                    delta = minV[j]
                    j1 = j
                    
            for j in range(m):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minV[j] -= delta
            
            j0 = j1
        
        while j0 != 0:
            p[j0] = p[way[j0]]
            j0 = way[j0]
    
    matching = [-1]*n
    for j in range(1,m):
        if p[j] != 0:
            matching[p[j]] = j
            
    return -v[0],matching