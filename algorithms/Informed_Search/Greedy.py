import time
from core.Game import apply_move, is_solved, grid_to_key, heuristic, extract_path, DIRECTIONS
from algorithms._base import Node, make_result
from queue import PriorityQueue

def solve_greedy(initial_grid):
    t0 = time.time()
    nodes = 0; max_dep = 0; counter = 0

    start = Node(initial_grid)
    frontier = PriorityQueue()
    frontier.put((heuristic(initial_grid), counter, start)) 
    in_frontier = {grid_to_key(initial_grid)}
    reached = set()

    while not frontier.empty():
        _, _, node = frontier.get()
        key = grid_to_key(node.grid)
        in_frontier.discard(key)

        nodes += 1
        if node.depth > max_dep:
            max_dep = node.depth

        if is_solved(node.grid):
            return make_result(extract_path(node), True, nodes, max_dep, time.time() - t0)

        reached.add(key)

        for move in DIRECTIONS:
            new_grid = apply_move(node.grid, move)
            if new_grid is None:
                continue
            new_key = grid_to_key(new_grid)

            if new_key not in reached and new_key not in in_frontier:
                counter += 1
                in_frontier.add(new_key)
                frontier.put((heuristic(new_grid), counter,
                              Node(new_grid, node, move, node.depth + 1)))

    return make_result([], False, nodes, max_dep, time.time() - t0)