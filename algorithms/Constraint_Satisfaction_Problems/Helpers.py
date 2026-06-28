from core.Game import EMPTY, GOAL, PLAYER, PLAYER_ON_GOAL, WALL

NUM_BOMBS   = 3
MIN_BLAST   = 1

BLAST_OFFSETS = [
    (-1,-1),(-1,0),(-1,1),
    ( 0,-1),       ( 0,1),
    ( 1,-1),( 1,0),( 1,1),
]

def blast_cells(r, c, grid):
    R, C = len(grid), len(grid[0])
    return {
        (r+dr, c+dc)
        for dr, dc in BLAST_OFFSETS
        if 0 <= r+dr < R and 0 <= c+dc < C and grid[r+dr][c+dc] == WALL
    }

def interior_walls(grid):
    R, C = len(grid), len(grid[0])
    return {
        (r, c)
        for r in range(1, R-1)
        for c in range(1, C-1)
        if grid[r][c] == WALL
    }

def floor_cells(grid):
    passable = {EMPTY, GOAL, PLAYER, PLAYER_ON_GOAL}
    R, C = len(grid), len(grid[0])
    return [
        (r, c)
        for r in range(1, R-1)
        for c in range(1, C-1)
        if grid[r][c] in passable
    ]

def score_position(pos, grid, target_walls):
    return len(blast_cells(*pos, grid) & target_walls)