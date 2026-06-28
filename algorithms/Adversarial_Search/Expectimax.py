import time
import copy
import random

from algorithms._base import make_result
from core.Game import (
    EMPTY, WALL, BOX, GOAL, BOX_ON_GOAL, DIRECTIONS, grid_to_key,
    apply_move, find_player, is_solved, heuristic, has_deadlock
)

SLIP_PROB         = 0.15   # 15% xác suất hộp trượt thêm 1 ô
NO_PROGRESS_LIMIT = 80

def evaluate(grid):
    if has_deadlock(grid): return -10_000
    boxes_on_goal = sum(row.count(BOX_ON_GOAL) for row in grid)
    raw = boxes_on_goal * 200 - heuristic(grid)
    return max(-9_000, raw)

def slip_box(grid, box_r, box_c, dr, dc):
    R, C = len(grid), len(grid[0])
    nr, nc = box_r + dr, box_c + dc
    if not (0 <= nr < R and 0 <= nc < C):
        return None
    dest = grid[nr][nc]
    if dest in (WALL, BOX, BOX_ON_GOAL):
        return None
    g = copy.deepcopy(grid)
    old = g[box_r][box_c]
    g[nr][nc] = BOX_ON_GOAL if dest == GOAL else BOX
    g[box_r][box_c] = GOAL if old == BOX_ON_GOAL else EMPTY
    return g

def get_outcomes(grid, direction):
    g_normal = apply_move(grid, direction)
    if g_normal is None: return []

    dr, dc = DIRECTIONS[direction]
    pr, pc = find_player(grid)
    nr, nc = pr + dr, pc + dc

    #Không đẩy hộp: xác suất 1.0, không có slip
    if grid[nr][nc] not in (BOX, BOX_ON_GOAL): return [(1.0, g_normal)]

    # Có đẩy hộp: tính các hướng slip hợp lệ
    box_r, box_c = nr + dr, nc + dc
    push_dir = (dr, dc)
    opposite = (-dr, -dc)

    valid_slips = []
    for sdr, sdc in DIRECTIONS.values():
        if (sdr, sdc) in (push_dir, opposite): continue
        g_slip = slip_box(g_normal, box_r, box_c, sdr, sdc)
        if g_slip is not None:
            valid_slips.append(g_slip)

    if not valid_slips: return [(1.0, g_normal)]

    slip_prob_each = SLIP_PROB / len(valid_slips)
    result = [(1.0 - SLIP_PROB, g_normal)]
    for g_slip in valid_slips:
        result.append((slip_prob_each, g_slip))
    return result

def boxes_on_goal_count(grid):
    return sum(row.count(BOX_ON_GOAL) for row in grid)

def solve_expectimax(initial_grid, depth_limit=10):
    t0    = time.time()
    nodes = [0]
    trans_table = {}
    def chance_node(outcomes, depth):
        nodes[0] += 1
        ev = 0.0
        for prob, g in outcomes:
            if is_solved(g):
                child_val = 1_000 + depth - 1
            else:
                child_val = max_node(g, depth - 1)
            ev += prob * child_val
        return ev

    def max_node(grid, depth):
        nodes[0] += 1
        if is_solved(grid): return 1_000 + depth
        if has_deadlock(grid): return -10_000
        if depth == 0: return evaluate(grid)

        key = grid_to_key(grid)
        if key in trans_table:
            cached_depth, cached_val = trans_table[key]
            if cached_depth >= depth: return cached_val

        best = None
        all_deadlock = True

        for name in DIRECTIONS:
            outs = get_outcomes(grid, name)
            if not outs: continue

            #Mỗi action dẫn đến một CHANCE node
            ev = chance_node(outs, depth)
            branch_ok = (ev > -10_000)

            if branch_ok: all_deadlock = False
            if best is None or ev > best: best = ev

        result = -10_000 if all_deadlock else (best if best is not None else evaluate(grid))
        trans_table[key] = (depth, result)
        return result
    
    boxes_total = sum(row.count(BOX) + row.count(BOX_ON_GOAL) for row in initial_grid)
    step_limit  = max(300, boxes_total * 40)

    best_path = [(initial_grid, None)]
    best_boxes_done = boxes_on_goal_count(initial_grid)
    found = False

    for effective_depth in range(2, depth_limit + 1):
        if found: break

        current = initial_grid
        path = [(current, None)]
        visit_count = {grid_to_key(current): 1}
        no_progress = 0
        prev_done = boxes_on_goal_count(current)
        prev_h = heuristic(current)

        for _step in range(step_limit):
            if is_solved(current):
                found = True
                break

            best_name, best_val = None, None
            for name in DIRECTIONS:
                outs = get_outcomes(current, name)
                if not outs: continue

                ev = chance_node(outs, effective_depth)

                for prob, g in outs:
                    count = visit_count.get(grid_to_key(g), 0)
                    ev   -= prob * (count ** 2) * 15

                if best_val is None or ev > best_val:
                    best_val, best_name = ev, name

            if best_name is None: break
            outs = get_outcomes(current, best_name)
            rnd = random.random()
            cumulative = 0.0
            chosen = outs[-1][1]
            slipped = len(outs) > 1
            for i, (prob, g) in enumerate(outs):
                cumulative += prob
                if rnd <= cumulative:
                    chosen = g
                    slipped = (i > 0)
                    break

            key = grid_to_key(chosen)
            visit_count[key] = visit_count.get(key, 0) + 1

            label = best_name + (" (trượt!)" if slipped else "")
            current = chosen
            path.append((current, label))
            cur_done = boxes_on_goal_count(current)
            cur_h    = heuristic(current)

            if cur_done > prev_done or cur_h < prev_h:
                no_progress = 0
                prev_done = cur_done
                prev_h = cur_h
            else:
                no_progress += 1
                if no_progress >= NO_PROGRESS_LIMIT: break

        cur_done = boxes_on_goal_count(current)
        if found:
            best_path = path
            best_boxes_done = boxes_total
        elif cur_done > best_boxes_done:
            best_boxes_done = cur_done
            best_path = path

    return make_result(best_path, found, nodes[0], depth_limit, time.time() - t0)