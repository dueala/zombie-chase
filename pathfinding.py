from collections import deque
from config import ROWS

def get_path(start, target, grid):
    """BFS pathfinding algorithm to find path from start to target"""
    queue = deque([(start, [])])
    visited = {tuple(start)}
    while queue:
        (r, c), path = queue.popleft()
        if [r, c] == target:
            return path[0] if path else None
        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        import random
        random.shuffle(dirs)
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < ROWS and grid[nr][nc] == "." and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), path + [[nr, nc]]))
    return None
