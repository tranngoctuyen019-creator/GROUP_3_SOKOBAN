import time
from collections import deque

from core.Game import ( apply_move, is_solved, grid_to_key, find_player, DIRECTIONS, WALL,)
from algorithms._base import make_result


def get_visible_cells(grid, radius=2):
    pos = find_player(grid)
    if pos is None:
        return set()
    pr, pc = pos
    R, C = len(grid), len(grid[0])
    visible = {(pr, pc)}
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            r, c = pr + dr, pc + dc
            if not (0 <= r < R and 0 <= c < C):
                continue
            steps = max(abs(dr), abs(dc))
            if steps == 0:
                visible.add((r, c))
                continue
            blocked = False
            for s in range(1, steps):
                ir = pr + round(dr * s / steps)
                ic = pc + round(dc * s / steps)
                if (
                    0 <= ir < R
                    and 0 <= ic < C
                    and grid[ir][ic] == WALL
                ):
                    blocked = True
                    break
            if not blocked:
                visible.add((r, c))

    return visible


def solve_partial_observation(initial_grid, vision_radius=2):
    """
    BFS với tầm nhìn giới hạn bán kính 2 ô.
    """
    t0 = time.time()
    nodes = 0

    class Node:
        __slots__ = ("grid", "parent", "move", "visible")

        def __init__(self, g, p=None, m=None, vis=None):
            self.grid = g
            self.parent = p
            self.move = m
            self.visible = vis

    def extract(node):
        path = []
        while node:
            path.append((node.grid, node.move, node.visible))
            node = node.parent
        path.reverse()
        return path
    
    start = Node(
        initial_grid,
        vis=get_visible_cells(initial_grid, vision_radius),
    )

    queue = deque([start])
    visited = {grid_to_key(initial_grid)}

    while queue:
        node = queue.popleft()
        nodes += 1
        if is_solved(node.grid):
            raw = extract(node)
            path = [(g, m) for g, m, v in raw]
            vis_list = [v for g, m, v in raw]
            cost = len(path) - 1
            return make_result(
                path,
                True,
                nodes,
                cost,
                time.time() - t0,
                {
                    "visible_list": vis_list,
                    "vision_radius": vision_radius,
                },
            )
        
        for move in DIRECTIONS:
            ng = apply_move(node.grid, move)
            if ng is None:
                continue
            nk = grid_to_key(ng)
            if nk in visited:
                continue
            visited.add(nk)
            vis = get_visible_cells(
                ng,
                vision_radius,
            )
            queue.append(
                Node(
                    ng,
                    node,
                    move,
                    vis,
                )
            )

    return make_result(
        [],
        False, nodes, 0,
        time.time() - t0,
        {  "vision_radius": vision_radius, },
    )