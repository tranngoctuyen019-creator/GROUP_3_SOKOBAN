import time

from core.Game import (
    apply_move,
    clone,
    heuristic,
    is_solved,
    DIRECTIONS,
    PLAYER2,
    PLAYER2_ON_GOAL,
)
from algorithms._base import Node, make_result
from algorithms.Adversarial_Search.Astar_Adversarial import solve_astar_adversarial

def _is_adversarial_map(grid):
    for row in grid:
        for v in row:
            if v in (PLAYER2, PLAYER2_ON_GOAL):
                return True
    return False

def solve_minimax(initial_grid, max_depth=6):
    t0 = time.time()
    if not _is_adversarial_map(initial_grid):
        return make_result([], False, 0, 0, time.time() - t0)

    start = clone(initial_grid)

    def evaluate(grid):
        if is_solved(grid):
            return 1000
        return -heuristic(grid)

    def next_states(grid, player_id):
        states = []
        for move in DIRECTIONS:
            new_grid = apply_move(grid, move, player_id)
            if new_grid is not None:
                states.append((move, new_grid))
        return states

    def minimax(grid, depth, maximizing_player):
        if depth == 0 or is_solved(grid):
            return evaluate(grid), None

        player_id = 1 if maximizing_player else 2
        best_move = None

        if maximizing_player:
            best_value = float("-inf")
            for move, child in next_states(grid, player_id):
                val, _ = minimax(child, depth - 1, False)
                if val > best_value:
                    best_value = val
                    best_move = move
            return best_value, best_move
        else:
            moves = next_states(grid, 2)
            if not moves:
                return evaluate(grid), None
            
            astar_pref = None
            try:
                result = solve_astar_adversarial(grid, player_id=2)
                if result and result.get("path") and len(result["path"]) > 1:
                    astar_pref = result["path"][1][1]
            except Exception:
                astar_pref = None

            if astar_pref is not None:
                ordered = []
                for m, child in moves:
                    if m == astar_pref:
                        ordered.insert(0, (m, child))
                    else:
                        ordered.append((m, child))
                moves = ordered

            best_value = float("inf")
            best_move = None
            for m, child in moves:
                val, _ = minimax(child, depth - 1, True)
                if val < best_value:
                    best_value = val
                    best_move = m
            return best_value, best_move

    path = [(start, None)]
    current = start
    winner = None
    nodes = 0
    max_dep = 0

    for turn in range(1, max_depth * 2 + 1):
        if is_solved(current):
            break

        if turn % 2 == 1:
            _, move = minimax(current, max_depth, True)
            if move is None:
                break
            current = apply_move(current, move, 1)
            nodes += 1
            if current is None:
                break
            path.append((current, move))
            if is_solved(current):
                winner = "Minimax"
                break
        else:
            result = solve_astar_adversarial(current, player_id=2)
            if not result.get("path") or len(result["path"]) < 2:
                moves = next_states(current, 2)
                if not moves:
                    break
                next_move, new_grid = moves[0]
            else:
                next_move = result["path"][1][1]
                if next_move is None:
                    moves = next_states(current, 2)
                    if not moves:
                        break
                    next_move, new_grid = moves[0]
                else:
                    new_grid = apply_move(current, next_move, 2)
            current = new_grid
            nodes += 1
            if current is None:
                break
            path.append((current, next_move))
            if is_solved(current):
                winner = "A*"
                break

    if winner is None and is_solved(current):
        winner = "Minimax" if len(path) % 2 == 1 else "A*"

    if winner is None:
        winner = "Không có"

    return make_result(path, is_solved(current), nodes, len(path) - 1,
                       time.time() - t0,
                       extra={"winner": winner, "mode": "adversarial_minimax"})
