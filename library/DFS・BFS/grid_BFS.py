from collections import deque
inf = 1001001001001001001

def grid_BFS(grid, start, goal = (-1,-1), transision = DIR_4):
    sx,sy = start
    gx,gy = goal
    
    que = deque()
    que.append((sx,sy))
    
    h,w = len(grid),len(grid[0])
    
    dis = [[inf]*w for i in range(h)]
    dis[sx][sy] = 0
    
    while que:
        x,y = que.popleft()
        nowdis = dis[x][y]
        
        if x == gx and y == gy:
            return nowdis
        
        for dx,dy in transision:
            nx,ny = x+dx,y+dy
            if (not 0 <= nx < h) or (not 0 <= ny < w):
                continue
            
            if grid[nx][ny] == "#":
                continue
        
            if dis[nx][ny] <= nowdis+1:
                continue
            
            dis[nx][ny] = nowdis+1
            que.append((nx,ny))
    
    return dis