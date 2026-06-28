# algorithms/informed/astar.py
# A* Search

import time
import heapq
from core.Game import apply_move, is_solved, grid_to_key, heuristic, extract_path, DIRECTIONS
from algorithms._base import Node, make_result

def solve_astar(initial_grid, player_id=1):
    """
    A* Search.
    f(n) = g(n) + h(n).
    """
    t0 = time.time()
    nodes = 0; max_dep = 0; counter = 0

    start = Node(initial_grid, cost=0)
    heap  = [(heuristic(initial_grid), counter, start)]
    
    # Khởi tạo visited và ghi nhận ngay trạng thái đầu tiên
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
            new_g   = node.cost + 1
            
            # Kiểm tra và cập nhật ngay lập tức trước khi push vào heap để tránh trùng lặp
            if new_key not in visited or visited[new_key] > new_g:
                visited[new_key] = new_g
                counter += 1
                heapq.heappush(heap, (new_g + heuristic(new_grid), counter,
                                      Node(new_grid, node, move, node.depth + 1, new_g)))

    return make_result([], False, nodes, max_dep, time.time() - t0)