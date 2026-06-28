import time

from core.Game import (
    apply_move,
    clone,
    find_boxes,
    grid_to_key,
    heuristic,
    is_solved,
    DIRECTIONS,
)
from algorithms._base import Node, make_result
from algorithms.Adversarial_Search.Astar_Adversarial import solve_astar_adversarial


def solve_alphabeta(initial_grid, max_depth=9):
    """
    Chơi đối kháng 2 robot trên một bản đồ: robot 1 dùng Alpha-Beta,
    robot 2 dùng A*.

    Luật:
    - Lượt đi luân phiên: Alpha-Beta trước, sau đó A*.
    - Robot nào đẩy được thùng vào đích trước thì thắng.
    - Mục tiêu là tìm đường đi cho cả hai robot trong một số bước cố định.
    """
    t0 = time.time()
    start = clone(initial_grid)

    def evaluate(grid):
        # Giá trị càng cao càng tốt cho robot Alpha-Beta.
        # Độ ưu tiên: Alpha-Beta thắng nhanh, A* thắng chậm.
        if is_solved(grid):
            return 1000

        box_positions = find_boxes(grid)
        if not box_positions:
            return 0

        score = -heuristic(grid)
        return score

    def next_states(grid, player_id):
        states = []
        for move in DIRECTIONS:
            new_grid = apply_move(grid, move, player_id)
            if new_grid is not None:
                states.append((move, new_grid))
        return states

    def alphabeta(grid, depth, alpha, beta, maximizing_player):
        if depth == 0 or is_solved(grid):
            return evaluate(grid), None

        player_id = 1 if maximizing_player else 2
        best_move = None

        if maximizing_player:
            value = float("-inf")
            for move, child in next_states(grid, player_id):
                child_value, _ = alphabeta(child, depth - 1, alpha, beta, False)
                if child_value > value:
                    value = child_value
                    best_move = move
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value, best_move
        else:
            value = float("inf")
            for move, child in next_states(grid, player_id):
                child_value, _ = alphabeta(child, depth - 1, alpha, beta, True)
                if child_value < value:
                    value = child_value
                    best_move = move
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value, best_move

    path = [(start, None)]
    current = start
    winner = None
    nodes = 0
    max_dep = 0

    for turn in range(1, max_depth * 2 + 1):
        if is_solved(current):
            break

        if turn % 2 == 1:
            _, move = alphabeta(current, max_depth, float("-inf"), float("inf"), True)
            if move is None:
                break
            current = apply_move(current, move, 1)
            nodes += 1
            if current is None:
                break
            path.append((current, move))
            if is_solved(current):
                winner = "Alpha-Beta"
                break
        else:
            result = solve_astar_adversarial(current, player_id=2)
            if not result["path"] or len(result["path"]) < 2:
                break
            next_step = result["path"][1][1]
            if next_step is None:
                break
            current = apply_move(current, next_step, 2)
            nodes += 1
            if current is None:
                break
            path.append((current, next_step))
            if is_solved(current):
                winner = "A*"
                break

    if winner is None and is_solved(current):
        winner = "Alpha-Beta" if len(path) % 2 == 1 else "A*"

    if winner is None:
        winner = "Không có"

    return make_result(path, is_solved(current), nodes, len(path) - 1,
                       time.time() - t0,
                       extra={"winner": winner, "mode": "adversarial"})
