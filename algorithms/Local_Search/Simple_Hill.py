import time
from core.Game import apply_move, is_solved, grid_to_key, DIRECTIONS, heuristic
from algorithms._base import make_result


def solve_hill_climbing(initial_grid, max_steps=2000):
    """
    Simple Hill Climbing
    Chọn trạng thái đầu tiên tốt hơn hiện tại.
    """
    t0 = time.time()

    nodes = 0
    depth = 0

    path = [(initial_grid, None)]
    current = initial_grid
    visited = {grid_to_key(initial_grid)}

    for step in range(max_steps):
        if is_solved(current):
            return make_result(
                path,
                True,
                nodes,
                depth,
                time.time() - t0
            )

        current_h = heuristic(current)
        best_child = None
        best_move = None

        for move, direction in DIRECTIONS.items():
            ng = apply_move(current, direction)
            if ng is None:
                continue
            
            nodes += 1
            key = grid_to_key(ng)
            if key in visited:
                continue

            child_h = heuristic(ng)
            if child_h <= current_h:
                best_child = ng
                best_move = move
                break

        if best_child is None:
            break
        visited.add(grid_to_key(best_child))
        path.append((best_child, best_move))
        current = best_child
        depth = max(depth, step + 1)

    return make_result(
        path,
        is_solved(current),
        nodes,
        depth,
        time.time() - t0
    )
