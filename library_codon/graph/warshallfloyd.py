def warshallfloyd(dis:list[list[int]]):
    n = len(dis)
    for i in range(n): dis[i][i] = 0

    for k in range(n):
        for i in range(n):
            for j in range(n):
                dis[i][j] = min(dis[i][j], dis[i][k]+dis[k][j])
    return dis
