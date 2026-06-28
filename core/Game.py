              
                                                
                            

import copy
import math
from itertools import permutations
                                                                 
EMPTY            = 0
WALL             = 1
PLAYER           = 2
BOX              = 3
GOAL             = 4
BOX_ON_GOAL      = 5
PLAYER_ON_GOAL   = 6
PLAYER2          = 7
PLAYER2_ON_GOAL  = 8

                                                                 
DIRECTIONS = {
    "UP":    (-1,  0),
    "DOWN":  ( 1,  0),
    "LEFT":  ( 0, -1),
    "RIGHT": ( 0,  1),
}

                                                                 

def find_player(grid, player_id=1):
    target = (PLAYER, PLAYER_ON_GOAL) if player_id == 1 else (PLAYER2, PLAYER2_ON_GOAL)
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v in target:
                return r, c
    return None

def find_players(grid):
    return find_player(grid, 1), find_player(grid, 2)


def find_boxes(grid):
    boxes = []
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v in (BOX, BOX_ON_GOAL):
                boxes.append((r, c))
    return boxes

def find_goals(grid):
    goals = []
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v in (GOAL, BOX_ON_GOAL, PLAYER_ON_GOAL, PLAYER2_ON_GOAL):
                goals.append((r, c))
    return goals

def is_solved(grid):
    return all(BOX not in row for row in grid)

def grid_to_key(grid):
    return tuple(tuple(row) for row in grid)

def clone(grid):
    return copy.deepcopy(grid)

                                                                 

def apply_move(grid, direction, player_id=1):
    """
    Áp dụng di chuyển của người chơi chỉ định.
    Trả về grid mới nếu hợp lệ, None nếu không hợp lệ.
    """
    if isinstance(direction, str):
        dr, dc = DIRECTIONS[direction]
    else:
        dr, dc = direction

    grid = copy.deepcopy(grid)
    R, C = len(grid), len(grid[0])
    pr, pc = find_player(grid, player_id)
    if pr is None:
        return None

    nr, nc = pr + dr, pc + dc

    if not (0 <= nr < R and 0 <= nc < C):
        return None
    if grid[nr][nc] == WALL:
        return None
    if grid[nr][nc] in (PLAYER, PLAYER_ON_GOAL, PLAYER2, PLAYER2_ON_GOAL):
        return None

    if grid[nr][nc] in (BOX, BOX_ON_GOAL):
        br, bc = nr + dr, nc + dc
        if not (0 <= br < R and 0 <= bc < C):
            return None
        if grid[br][bc] in (WALL, BOX, BOX_ON_GOAL,
                            PLAYER, PLAYER_ON_GOAL,
                            PLAYER2, PLAYER2_ON_GOAL):
            return None
        old_box = grid[nr][nc]
        grid[br][bc] = BOX_ON_GOAL if grid[br][bc] == GOAL else BOX
        grid[nr][nc] = GOAL if old_box == BOX_ON_GOAL else EMPTY

    old_player = grid[pr][pc]
    dest       = grid[nr][nc]
    grid[pr][pc] = GOAL if old_player in (PLAYER_ON_GOAL, PLAYER2_ON_GOAL) else EMPTY

    if player_id == 1:
        grid[nr][nc] = PLAYER_ON_GOAL if dest == GOAL else PLAYER
    else:
        grid[nr][nc] = PLAYER2_ON_GOAL if dest == GOAL else PLAYER2

    return grid

def get_valid_moves(grid, player_id=1):
    return [d for d in DIRECTIONS if apply_move(grid, d, player_id) is not None]

def get_push_positions(box):
    r, c = box
    return [
        (r + 1, c),
        (r - 1, c),
        (r, c + 1),
        (r, c - 1),
    ]

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def is_corner_deadlock(grid, box, goals):
    if box in goals:
        return False

    r, c = box
    R, C = len(grid), len(grid[0])

    wall_up    = (r == 0) or (grid[r-1][c] == WALL)
    wall_down  = (r == R-1) or (grid[r+1][c] == WALL)
    wall_left  = (c == 0) or (grid[r][c-1] == WALL)
    wall_right = (c == C-1) or (grid[r][c+1] == WALL)

    return (wall_up or wall_down) and (wall_left or wall_right)

def heuristic(grid):
    boxes = find_boxes(grid)
    goals = find_goals(grid)
    player = find_player(grid)

    if not boxes: return 0
    for b in boxes:
        if is_corner_deadlock(grid, b, goals): return float('inf')

    box_goal_cost = float('inf')

    for perm in permutations(goals, len(boxes)):
        cost = 0
        for b, g in zip(boxes, perm):
            cost += manhattan(b, g)
        box_goal_cost = min(box_goal_cost, cost)

    player_push_cost = math.inf

    for b in boxes:
        for p in get_push_positions(b):
            player_push_cost = min(player_push_cost, manhattan(player, p))

    if player_push_cost == math.inf:
        player_push_cost = 0

    return box_goal_cost + 0.1 * player_push_cost


def has_deadlock(grid):
    goals = find_goals(grid)
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v == BOX and is_corner_deadlock(grid, (r, c), goals):
                return True

    return False

                                                                 

def extract_path(node):
    """
    node phải có .grid, .parent, .move
    Trả về list of (grid, move) từ đầu đến cuối.
    """
    path = []
    while node:
        path.append((node.grid, node.move))
        node = node.parent
    path.reverse()
    return path
