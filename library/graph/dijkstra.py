from heapq import heappop,heappush
def dijkstra(edge:list[set[int]], start:int = 0, goal:int = None):
    """
    O((node+edge)log(edge))
    """
    n = len(edge)
    dis = [inf]*n
    dis[start] = 0
    que = [(0, start)]
  
    while que:
        cur_dis,cur_node = heappop(que)

        if dis[cur_node] < cur_dis:
            continue

        for next_node, weight in edge[cur_node]:
            next_dis = cur_dis + weight

            if next_dis < dis[next_node]:
                dis[next_node] = next_dis
                heappush(que, (next_dis, next_node))
    
    if goal != None: return dis[goal]
    return dis
