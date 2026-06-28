import copy, time, itertools
from collections import deque

from core.Game import (
    EMPTY, WALL, PLAYER, BOX, GOAL, BOX_ON_GOAL, PLAYER_ON_GOAL,
    find_player, find_boxes,
    apply_move, grid_to_key, DIRECTIONS,
)
from algorithms._base import make_result
from algorithms.Constraint_Satisfaction_Problems.Helpers import floor_cells, NUM_BOMBS, BLAST_OFFSETS
from algorithms.Constraint_Satisfaction_Problems.Backtracking_Search import solve_backtracking
from algorithms.Constraint_Satisfaction_Problems.Forward_Checking import solve_forward_checking
from algorithms.Constraint_Satisfaction_Problems.Min_Conflicts import solve_min_conflicts

BOMB      = 10
BOMB_GOAL = 11
EXPLODED  = 12

def make_bomb_grid(base_grid, bomb_starts):
    g = copy.deepcopy(base_grid)
    for r, row in enumerate(g):
        for c, v in enumerate(row):
            if v == BOX:           g[r][c] = EMPTY
            elif v == BOX_ON_GOAL: g[r][c] = GOAL
    for r, row in enumerate(g):
        for c, v in enumerate(row):
            if v == GOAL:             g[r][c] = EMPTY
            elif v == PLAYER_ON_GOAL: g[r][c] = PLAYER
    for br, bc in bomb_starts:
        if g[br][bc] == EMPTY:
            g[br][bc] = BOX
    return g

def bfs_push_bomb(full_grid, active_bomb, other_bombs, target_pos):
    if active_bomb == target_pos:
        return [full_grid]

    g_single = copy.deepcopy(full_grid)
    for br, bc in other_bombs:
        v = g_single[br][bc]
        if v == BOX:           g_single[br][bc] = WALL
        elif v == BOX_ON_GOAL: g_single[br][bc] = GOAL

    queue = deque([(g_single, [g_single])])
    visited = {grid_to_key(g_single)}

    while queue:
        cur, path = queue.popleft()
        for move in DIRECTIONS:
            ng = apply_move(cur, move)
            if ng is None:
                continue
            key = grid_to_key(ng)
            if key in visited:
                continue
            visited.add(key)
            new_path = path + [ng]
            if target_pos in find_boxes(ng):
                result = []
                for sg in new_path:
                    fg = copy.deepcopy(sg)
                    for br, bc in other_bombs:
                        cell = fg[br][bc]
                        if cell == WALL:   fg[br][bc] = BOX
                        elif cell == GOAL: fg[br][bc] = BOX_ON_GOAL
                    result.append(fg)
                return result
            queue.append((ng, new_path))
    return []

def bfs_player_to_safe(grid, bomb_positions):
    danger = set(bomb_positions)
    for r, c in bomb_positions:
        for dr, dc in BLAST_OFFSETS:
            danger.add((r+dr, c+dc))

    pr, pc = find_player(grid)
    if (pr, pc) not in danger:
        return [grid]

    queue = deque([(grid, [grid])])
    visited = {grid_to_key(grid)}

    while queue:
        cur, path = queue.popleft()
        for move in DIRECTIONS:
            ng = apply_move(cur, move)
            if ng is None:
                continue
            key = grid_to_key(ng)
            if key in visited:
                continue
            visited.add(key)
            npr, npc = find_player(ng)
            new_path = path + [ng]
            if (npr, npc) not in danger:
                return new_path
            queue.append((ng, new_path))
    return [grid]

def apply_explosions(grid, bomb_positions):
    g = copy.deepcopy(grid)
    R, C = len(g), len(g[0])
    for br, bc in bomb_positions:
        if g[br][bc] in (BOX, BOX_ON_GOAL, BOMB, BOMB_GOAL):
            g[br][bc] = EMPTY
        for dr, dc in BLAST_OFFSETS:
            nr, nc = br+dr, bc+dc
            if 0 <= nr < R and 0 <= nc < C and g[nr][nc] == WALL:
                g[nr][nc] = EXPLODED
    return g

def execute_assignment(initial_grid, assignment, t0):
    target_positions = [assignment[i] for i in range(NUM_BOMBS)]

    original_boxes = find_boxes(initial_grid)
    floors = floor_cells(initial_grid)
    pr, pc = find_player(initial_grid)

    if len(original_boxes) >= NUM_BOMBS:
        bomb_starts = original_boxes[:NUM_BOMBS]
    else:
        extras = sorted(
            [f for f in floors if f != (pr, pc) and f not in original_boxes],
            key=lambda p: abs(p[0]-pr)+abs(p[1]-pc)
        )
        bomb_starts = (original_boxes + extras)[:NUM_BOMBS]

    work_grid = make_bomb_grid(initial_grid, bomb_starts)

    success_path, success_grid = None, None
    for perm in itertools.permutations(target_positions):
        cur = work_grid
        path_attempt = [work_grid]
        placed = []
        ok = True
        for target in perm:
            cur_boxes = find_boxes(cur)
            if target in cur_boxes:
                placed.append(target)
                continue
            unplaced = [b for b in cur_boxes if b not in placed]
            pushed = False
            for candidate in sorted(unplaced,
                    key=lambda b: abs(b[0]-target[0])+abs(b[1]-target[1])):
                others = [b for b in cur_boxes if b != candidate]
                sub = bfs_push_bomb(cur, candidate, others, target)
                if sub and target in find_boxes(sub[-1]):
                    path_attempt.extend(sub[1:])
                    cur = sub[-1]
                    placed.append(target)
                    pushed = True
                    break
            if not pushed:
                ok = False
                break
        if ok:
            success_path, success_grid = path_attempt, cur
            break

    full_path = success_path or [work_grid]
    cur_grid  = success_grid or work_grid

    safety = bfs_player_to_safe(cur_grid, target_positions)
    full_path.extend(safety[1:])

    exploded = apply_explosions(safety[-1], target_positions)
    full_path.append(exploded)
    explosion_step = len(full_path) - 1

    path_fmt = [(full_path[0], None)] + [
        (full_path[i], f"STEP_{i}") for i in range(1, len(full_path))
    ]
    return make_result(
        path_fmt, True, len(path_fmt), explosion_step, time.time() - t0,
        {
            "mode":           "bomb",
            "bomb_positions": target_positions,
            "explosion_step": explosion_step,
            "assignment":     {f"bomb_{i}": str(assignment[i]) for i in range(NUM_BOMBS)},
        }
    )


def no_solution(t0):
    return make_result([], False, 0, 0, time.time() - t0,
                       {"mode": "bomb", "bomb_positions": [], "explosion_step": 0})


def solve_bomb_backtracking(initial_grid):
    t0 = time.time()
    assignment = solve_backtracking(initial_grid)
    if not assignment:
        return no_solution(t0)
    return execute_assignment(initial_grid, assignment, t0)


def solve_bomb_forward_checking(initial_grid):
    t0 = time.time()
    assignment = solve_forward_checking(initial_grid)
    if not assignment:
        return no_solution(t0)
    return execute_assignment(initial_grid, assignment, t0)


def solve_bomb_min_conflicts(initial_grid):
    t0 = time.time()
    assignment = solve_min_conflicts(initial_grid)
    if not assignment:
        return no_solution(t0)
    return execute_assignment(initial_grid, assignment, t0)