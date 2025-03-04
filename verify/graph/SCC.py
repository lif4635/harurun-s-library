# https://atcoder.jp/contests/practice2/submissions/63383085

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

def SCC_construct(edge):
    n = len(edge)
    label, group = SCC(edge)
    newedge = [set() for i in range(label)]
    groups = [[] for i in range(label)]
    for u in range(n):
        lu = group[u]
        for v in edge[u]:
            lv = group[v]
            if lu == lv: continue
            newedge[lu].add(lv)
        groups[lu].append(u)
    return newedge, groups

n,m = map(int, input().split())
edge = [set() for i in range(n)]
for i in range(m):
    a,b = map(int, input().split())
    edge[a].add(b)
newedge, groups = SCC_construct(edge)

print(len(groups))
for g in groups:
    print(len(g), *g)