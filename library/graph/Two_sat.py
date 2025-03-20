def SCC(edge):
    n = len(edge)
    redge = [set() for i in range(n)]
    for u in range(n):
        for v in edge[u]:
            redge[v].add(u)
    
    used = [0]*n
    order = []
    for i in range(n):
        if used[i] == 0:
            que = [~i, i]
            while que:
                u = que.pop()
                if u >= 0:
                    if used[u] == 0:
                        used[u] = 1
                        for v in edge[u]:
                            que.append(~v)
                            que.append(v)
                    else:
                        que.pop()
                else:
                    order.append(~u)
    label = 0
    group = [-1]*n
    que = []
    for i in reversed(order):
        if group[i] == -1:
            que.append(i)
            group[i] = label
            while que:
                u = que.pop()
                for v in redge[u]:
                    if group[v] == -1:
                        que.append(v)
                        group[v] = label
            label += 1
    return label, group

def Twosat(n, clause):
    edge = [[] for i in range(2 * n)]
    for i,f,j,g in clause:
        edge[2 * i + 1 - f].append(2 * j + g)
        edge[2 * j + 1 - g].append(2 * i + f)
    _, group = SCC(edge)
    answer = [0] * n
    for i in range(n):
        if group[2 * i] == group[2 * i + 1]:
            return None
        answer[i] = group[2 * i] < group[2 * i + 1]
    return answer