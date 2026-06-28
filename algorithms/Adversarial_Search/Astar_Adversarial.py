import time
import heapq

from core.Game import (
    apply_move,
    extract_path,
    grid_to_key,
    heuristic,
    is_solved,
    DIRECTIONS,
)
from algorithms._base import Node, make_result


def solve_astar_adversarial(initial_grid, player_id=2):
    """
    A* cho robot đối kháng.

    Nếu không tìm được đường giải, vẫn trả về một bước hợp lệ đầu tiên.
    """
    t0 = time.time()
    nodes = 0
    max_dep = 0
    counter = 0

    start = Node(initial_grid, cost=0)
    heap = [(heuristic(initial_grid), counter, start)]
    visited = {grid_to_key(initial_grid): 0}

    while heap:
        _, _, node = heapq.heappop(heap)
        nodes += 1
        if node.depth > max_dep:
            max_dep = node.depth

        if is_solved(node.grid):
            return make_result(extract_path(node), True, nodes, max_dep, time.time() - t0)

        for move in DIRECTIONS:
            new_grid = apply_move(node.grid, move, player_id)
            if new_grid is None:
                continue

            new_key = grid_to_key(new_grid)
            new_g = node.cost + 1

            if new_key not in visited or visited[new_key] > new_g:
                visited[new_key] = new_g
                counter += 1
                heapq.heappush(
                    heap,
                    (new_g + heuristic(new_grid), counter,
                     Node(new_grid, node, move, node.depth + 1, new_g))
                )

    # Nếu không tìm thấy lời giải, chọn một bước hợp lệ đầu tiên
    fallback_moves = []
    for move in DIRECTIONS:
        new_grid = apply_move(initial_grid, move, player_id)
        if new_grid is not None:
            fallback_moves.append((move, new_grid))

    if fallback_moves:
        move, new_grid = fallback_moves[0]
        path = [(initial_grid, None), (new_grid, move)]
        return make_result(path, False, nodes, max_dep, time.time() - t0)

    return make_result([(initial_grid, None)], False, nodes, max_dep, time.time() - t0)
