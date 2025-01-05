inf = 1001001001001001001

def bellmanford(edge:list[set[int]], start:int = 0, goal:int = None):
    n = len(edge)
    dis = [inf]*n
    dis[start] = 0
  
    for t in range(2*n):
        for u in range(n):
            for v, cost in edge[u]:
                if dis[v] > dis[u] + cost and dis[u] < inf:
                    if t >= n-1:
                        dis[v] = -inf
                    else:
                        dis[v] = dis[u] + cost

    if goal != None: return dis[goal]
    return dis
