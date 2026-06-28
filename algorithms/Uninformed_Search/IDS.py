# algorithms/uninformed/ids.py
# Iterative Deepening Search

import time
from core.Game import apply_move, is_solved, grid_to_key, extract_path, DIRECTIONS
from algorithms._base import Node, make_result


def _dls(initial_grid, limit, stats):
    """
    Depth-Limited Search (Tìm kiếm giới hạn độ sâu).
    Bổ trợ cho IDS để duyệt từng tầng.
    """
    start = Node(initial_grid)
    if is_solved(start.grid):
        return start, False

    stack = [start]
    visited = {grid_to_key(initial_grid): 0}
    any_remaining = False

    while stack:
        node = stack.pop()
        stats["nodes"] += 1
        
        if node.depth > stats["max_dep"]:
            stats["max_dep"] = node.depth

        if is_solved(node.grid):
            return node, False

        if node.depth >= limit:
            any_remaining = True
            continue

        for move in DIRECTIONS:
            new_grid = apply_move(node.grid, move)
            if new_grid is None:
                continue
            
            key = grid_to_key(new_grid)
            next_depth = node.depth + 1

            if key in visited and visited[key] <= next_depth:
                continue

            visited[key] = next_depth
            stack.append(Node(new_grid, node, move, next_depth))

    return None, any_remaining


def solve_ids(initial_grid, max_limit=100):
    """
    Iterative Deepening Search.
    Tăng dần độ sâu giới hạn để tìm lời giải ngắn nhất bằng DFS.
    """
    t0 = time.time()
    stats = {"nodes": 0, "max_dep": 0}

    for limit in range(max_limit):
        found_node, any_remaining = _dls(initial_grid, limit, stats)

        if found_node is not None:
            return make_result(extract_path(found_node), True, stats["nodes"], stats["max_dep"], time.time() - t0)

        if not any_remaining:
            break

    return make_result([], False, stats["nodes"], stats["max_dep"], time.time() - t0)