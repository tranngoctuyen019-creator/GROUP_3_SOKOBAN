import time
from core.Game import apply_move, is_solved, grid_to_key, extract_path, DIRECTIONS
from algorithms._base import Node, make_result

MAX_DEPTH = 150

def solve_dfs(initial_grid):
    t0 = time.time()
    nodes = 0
    max_dep = 0

    start = Node(initial_grid)

    if is_solved(start.grid):
        return make_result(
            extract_path(start),
            True,
            1,
            0,
            time.time() - t0
        )

    frontier = [start]
    frontier_set = {grid_to_key(start.grid)}
    explored = set()

    while frontier:
        node = frontier.pop()
        nodes += 1

        key = grid_to_key(node.grid)
        frontier_set.remove(key)
        explored.add(key)

        if node.depth > max_dep:
            max_dep = node.depth

        if node.depth >= MAX_DEPTH:
            continue

        for move in DIRECTIONS:
            new_grid = apply_move(node.grid, move)

            if new_grid is None:
                continue

            new_key = grid_to_key(new_grid)
            if new_key not in explored and new_key not in frontier_set:
                child = Node( new_grid, node, move, node.depth + 1)

                if is_solved(child.grid):
                    return make_result(
                        extract_path(child),
                        True,
                        nodes,
                        max_dep,
                        time.time() - t0
                    )
                frontier.append(child)
                frontier_set.add(new_key)

    return make_result(
        [],
        False,
        nodes,
        max_dep,
        time.time() - t0
    )