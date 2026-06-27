# algorithms/_base.py
# Shared base classes and helpers for all algorithm modules

class Node:
    __slots__ = ("grid", "parent", "move", "depth", "cost")

    def __init__(self, grid, parent=None, move=None, depth=0, cost=0):
        self.grid   = grid
        self.parent = parent
        self.move   = move
        self.depth  = depth
        self.cost   = cost


def make_result(path, found, nodes, depth, t, extra=None):
    r = {
        "path":          path,
        "found":         found,
        "nodes_visited": nodes,
        "max_depth":     depth,
        "solution_len":  len(path) - 1 if path else 0,
        "time_elapsed":  round(t, 4),
    }
    if extra:
        r.update(extra)
    return r
