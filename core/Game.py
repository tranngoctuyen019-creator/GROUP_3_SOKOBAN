# core/game.py
# Logic Sokoban dùng chung cho tất cả thuật toán
# KHÔNG import tkinter ở đây

import copy

# ── Ký hiệu ô ──────────────────────────────────────────────────
EMPTY          = 0
WALL           = 1
PLAYER         = 2
BOX            = 3
GOAL           = 4
BOX_ON_GOAL    = 5
PLAYER_ON_GOAL = 6

# ── Hướng di chuyển ────────────────────────────────────────────
DIRECTIONS = {
    "UP":    (-1,  0),
    "DOWN":  ( 1,  0),
    "LEFT":  ( 0, -1),
    "RIGHT": ( 0,  1),
}

# ── Trạng thái ─────────────────────────────────────────────────

def find_player(grid):
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v in (PLAYER, PLAYER_ON_GOAL):
                return r, c
    return None

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
            if v in (GOAL, BOX_ON_GOAL, PLAYER_ON_GOAL):
                goals.append((r, c))
    return goals

def is_solved(grid):
    return all(BOX not in row for row in grid)

def grid_to_key(grid):
    return tuple(tuple(row) for row in grid)

def clone(grid):
    return copy.deepcopy(grid)

# ── Di chuyển ──────────────────────────────────────────────────

def apply_move(grid, direction):
    """
    Áp dụng di chuyển theo tên hướng ("UP","DOWN","LEFT","RIGHT").
    Trả về grid mới nếu hợp lệ, None nếu không hợp lệ.
    """
    if isinstance(direction, str):
        dr, dc = DIRECTIONS[direction]
    else:
        dr, dc = direction

    grid = copy.deepcopy(grid)
    R, C = len(grid), len(grid[0])
    pr, pc = find_player(grid)
    nr, nc = pr + dr, pc + dc

    if not (0 <= nr < R and 0 <= nc < C):
        return None
    if grid[nr][nc] == WALL:
        return None

    if grid[nr][nc] in (BOX, BOX_ON_GOAL):
        br, bc = nr + dr, nc + dc
        if not (0 <= br < R and 0 <= bc < C):
            return None
        if grid[br][bc] in (WALL, BOX, BOX_ON_GOAL):
            return None
        old_box = grid[nr][nc]
        grid[br][bc] = BOX_ON_GOAL if grid[br][bc] == GOAL else BOX
        grid[nr][nc] = GOAL if old_box == BOX_ON_GOAL else EMPTY

    old_player = grid[pr][pc]
    dest       = grid[nr][nc]
    grid[pr][pc] = GOAL if old_player == PLAYER_ON_GOAL else EMPTY
    grid[nr][nc] = PLAYER_ON_GOAL if dest == GOAL else PLAYER

    return grid

def get_valid_moves(grid):
    return [d for d in DIRECTIONS if apply_move(grid, d) is not None]

# ── Heuristic ──────────────────────────────────────────────────

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def heuristic(grid):
    """
    Tổng khoảng cách Manhattan từ mỗi thùng đến đích gần nhất.
    Dùng cho: Greedy, A*, IDA*, Hill Climbing, Beam Search...
    """
    boxes = find_boxes(grid)
    goals = find_goals(grid)
    if not boxes:
        return 0
    total = 0
    for box in boxes:
        total += min(manhattan(box, g) for g in goals)
    return total

# ── Deadlock detection (dùng cho CSP) ─────────────────────────

def is_corner_deadlock(grid, r, c):
    if grid[r][c] == BOX_ON_GOAL:
        return False
    R, C = len(grid), len(grid[0])
    wall_v = (r == 0 or grid[r-1][c] == WALL) or \
             (r == R-1 or grid[r+1][c] == WALL)
    wall_h = (c == 0 or grid[r][c-1] == WALL) or \
             (c == C-1 or grid[r][c+1] == WALL)
    return wall_v and wall_h

def has_deadlock(grid):
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v == BOX and is_corner_deadlock(grid, r, c):
                return True
    return False

# ── Trích xuất đường đi từ node ────────────────────────────────

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
