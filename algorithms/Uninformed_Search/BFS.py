import time
from collections import deque
from core.Game import apply_move, is_solved, grid_to_key, extract_path, DIRECTIONS
from algorithms._base import Node, make_result


def solve_bfs(initial_grid):
    """
    Breadth-First Search.
    Đảm bảo tìm lời giải ngắn nhất (ít bước nhất).
    """
    t0 = time.time()
    nodes = 0
    max_dep = 0

    start = Node(initial_grid)

    frontier = deque([start])
    frontier_set = {grid_to_key(initial_grid)}
    explored = set()

    while frontier:
        node = frontier.popleft()
        frontier_set.remove(grid_to_key(node.grid))
        explored.add(grid_to_key(node.grid))

        nodes += 1
        if node.depth > max_dep:
            max_dep = node.depth

        if is_solved(node.grid):
            return make_result(
                extract_path(node),
                True,
                nodes,
                max_dep,
                time.time() - t0
            )

        for move in DIRECTIONS:
            new_grid = apply_move(node.grid, move)
            if new_grid is None:
                continue

            key = grid_to_key(new_grid)

            in_frontier = key in frontier_set

            if key not in explored and not in_frontier:
                child = Node(new_grid, node, move, node.depth + 1)

                if is_solved(new_grid):
                    return make_result(
                        extract_path(child),
                        True,
                        nodes,
                        max_dep,
                        time.time() - t0
                    )

                frontier.append(child)
                frontier_set.add(key)

    return make_result(
        [],
        False,
        nodes,
        max_dep,
        time.time() - t0
    )