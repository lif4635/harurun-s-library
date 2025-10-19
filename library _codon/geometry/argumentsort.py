def arg_sort(points:list[tuple[int]]):
    """
    0°closed
    """
    n = len(points)
    p = [(0,0)]*n
    pidx = -1
    nidx = n
    for x,y in points:
        if x == 0 and y == 0:
            pass
        elif y < 0 or (x > 0 and y == 0):
            pidx += 1
            p[pidx] = (x,y)
        else:
            nidx -= 1
            p[nidx] = (x,y)
    
    que = []
    if pidx != -1: que.append((0,pidx))
    if nidx != n: que.append((nidx,n-1)) 
    while que:
        i,j = que.pop()
        left,right = i,j
        pivot = (i+j)//2
        px,py = p[pivot]

        while True:
            while px*p[i][1] - py*p[i][0] < 0: i += 1
            while p[j][0]*py - p[j][1]*px < 0: j -= 1
            if i >= j: break
            p[i],p[j] = p[j],p[i]
            i += 1
            j -= 1
        
        if left < i-1: que.append((left, i-1))
        if right > j+1: que.append((j+1, right))
    
    return p
