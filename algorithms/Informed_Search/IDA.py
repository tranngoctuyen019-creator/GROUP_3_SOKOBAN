import time
from core.Game import (
    apply_move,
    is_solved,
    grid_to_key,
    heuristic,
    extract_path,
    DIRECTIONS,
)
from algorithms._base import Node, make_result


def solve_idastar(initial_grid, max_nodes=50000, max_threshold=1000):
    """
    Iterative Deepening A*.
    """

    t0 = time.time()
    nodes = [0]
    max_dep = [0]
    threshold = heuristic(initial_grid)
    start = Node(initial_grid)

    path = [start]
    path_keys = {grid_to_key(initial_grid)}

    # Lưu đường đi sâu nhất để hiển thị nếu không tìm thấy lời giải
    best_path = [start]

    def ida_dfs(path, g, threshold):
        nonlocal best_path
        node = path[-1]
        # Cập nhật đường đi sâu nhất
        if len(path) > len(best_path):
            best_path = path.copy()
        nodes[0] += 1

        if nodes[0] >= max_nodes:
            return float("inf")

        if g > max_dep[0]:
            max_dep[0] = g

        f = g + heuristic(node.grid)
        if f > threshold:
            return f
        if is_solved(node.grid):
            return "FOUND"

        minimum = float("inf")
        for move in DIRECTIONS:
            new_grid = apply_move(node.grid, move)
            if new_grid is None:
                continue
            key = grid_to_key(new_grid)
            if key in path_keys:
                continue
            child = Node(new_grid, node, move, g + 1)

            path.append(child)
            path_keys.add(key)

            result = ida_dfs(path, g + 1, threshold)

            if result == "FOUND":
                return "FOUND"
            minimum = min(minimum, result)
            path.pop()
            path_keys.remove(key)
        return minimum
    
    while threshold <= max_threshold:
        result = ida_dfs(path, 0, threshold)
        if result == "FOUND":
            return make_result(
                extract_path(path[-1]),
                True,
                nodes[0],
                max_dep[0],
                time.time() - t0,
            )
        if result == float("inf"):
            break
        threshold = result

    # Không tìm thấy lời giải -> trả về đường đi đã khám phá sâu nhất
    return make_result(
        extract_path(best_path[-1]),
        False,
        nodes[0],
        max_dep[0],
        time.time() - t0,
    )