import time
import random
import math
from core.Game import (apply_move, is_solved, heuristic, DIRECTIONS, grid_to_key, has_deadlock)
from algorithms._base import make_result

def solve_simulated_annealing(
    initial_grid,
    T=100,
    T_min=0.001,
    alpha=0.9999,
    max_steps=500_000,):

    t0 = time.time()
    nodes = 0

    current = initial_grid
    current_h = heuristic(current)
    came_from = {}  
    key_to_grid = {}  
    start_key = grid_to_key(current)
    came_from[start_key] = (None, None)
    key_to_grid[start_key] = current

    best_key = start_key
    best_h = current_h
    current_key = start_key

    T_cur = T

    def reconstruct(end_key):
        path = []
        k = end_key
        while came_from[k][0] is not None:
            prev_k, move = came_from[k]
            path.append((key_to_grid[k], move))
            k = prev_k
        path.append((key_to_grid[start_key], None))
        path.reverse()
        return path

    while T_cur > T_min and nodes < max_steps:
        if is_solved(current):
            path = reconstruct(current_key)
            return make_result(
                path, True, nodes, len(path) - 1,
                time.time() - t0,
                {"temperature": round(T_cur, 4)},
            )

        # Sinh neighbors hợp lệ
        moves = list(DIRECTIONS.keys())
        random.shuffle(moves)

        neighbors = []
        for move in moves:
            nxt = apply_move(current, move)
            if nxt is None:
                continue
            # Bỏ qua deadlock ngay lập tức
            if has_deadlock(nxt):
                continue
            neighbors.append((move, nxt))

        if not neighbors:
            # Bị kẹt hoàn toàn - restart từ best
            current_key = best_key
            current = key_to_grid[best_key]
            current_h = best_h
            T_cur = min(T_cur * 2, T)  
            continue

        move, next_state = random.choice(neighbors)
        nodes += 1

        next_h = heuristic(next_state)
        # Bỏ qua trạng thái deadlock (heuristic = inf)
        if next_h == float('inf'):
            T_cur *= alpha
            continue

        delta = next_h - current_h
        accept = delta < 0 or (
            random.random() < math.exp(-delta / max(T_cur, 1e-9))
        )

        if accept:
            next_key = grid_to_key(next_state)
            if next_key not in came_from: 
                came_from[next_key] = (current_key, move)
                key_to_grid[next_key] = next_state

            current = next_state
            current_key = next_key
            current_h = next_h

            if current_h < best_h:
                best_h = current_h
                best_key = current_key

        T_cur *= alpha

    # Trả về best tìm được dù chưa solved
    path = reconstruct(best_key)
    return make_result(
        path, is_solved(key_to_grid[best_key]),
        nodes, len(path) - 1,
        time.time() - t0,
        {"temperature": round(T_cur, 4)},
    )