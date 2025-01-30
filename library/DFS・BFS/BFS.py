from collections import deque
inf = 1001001001001001001

def BFS(start, edge):
    n = len(edge)
    dis = [inf]*n
    dis[start] = 0
    que = deque()
    que.append(start)
    while que:
        now = que.popleft()
        nowdis = dis[now]
        for chi in edge[now]:
            if dis[chi] <= nowdis+1:
                continue
            dis[chi] = nowdis+1
            que.append(chi)
    return dis