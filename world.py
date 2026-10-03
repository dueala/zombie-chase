import random
from config import ROWS, CELL_SIZE, C_TREE, C_TREE2, C_HOUSE, C_STONE, C_RUNE, C_WATER

class WorldObject:
    def __init__(self, r, c, obj_type):
        self.r, self.c, self.type = r, c, obj_type
        self.x, self.y = c*CELL_SIZE, r*CELL_SIZE
        self.seed = random.randint(0,1000)

def generate_world():
    """Generate world objects, collision grid, and lamp positions"""
    objects=[]; grid=[["." for _ in range(ROWS)] for _ in range(ROWS)]; lamps=[]
    rng=random.Random(99)
    for r in range(ROWS):
        for c in range(ROWS):
            if r==0 or r==ROWS-1 or c==0 or c==ROWS-1: grid[r][c]="T"
            elif rng.random()<0.10:
                obj_type=rng.choice(['tree','tree','tree','house','bush','stone'])
                objects.append(WorldObject(r,c,obj_type)); grid[r][c]="T"
            elif rng.random()<0.04:
                objects.append(WorldObject(r,c,'water')); grid[r][c]="W"
    for r in range(3,ROWS-3,7):
        for c in range(3,ROWS-3,7):
            if grid[r][c]==".": lamps.append([r,c])
    return objects, grid, lamps
