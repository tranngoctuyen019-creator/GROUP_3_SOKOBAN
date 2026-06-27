from algorithms.Constraint_Satisfaction_Problems.Helpers import (
    blast_cells, interior_walls, floor_cells,
    score_position, NUM_BOMBS, MIN_BLAST,
)


def solve_backtracking(grid):
    """
    Plain backtracking: enumerate all NUM_BOMBS-tuples of floor cells,
    keep the assignment that destroys the most interior walls.
    """
    candidates = floor_cells(grid)
    target_walls = interior_walls(grid)

    if len(candidates) < NUM_BOMBS:
        return None

    candidates.sort(key=lambda p: -score_position(p, grid, target_walls))

    best = {"assignment": None, "score": -1}

    def bt(var_idx, assignment):
        if var_idx == NUM_BOMBS:
            covered = set()
            for pos in assignment.values():
                covered |= (blast_cells(*pos, grid) & target_walls)
            sc = len(covered)
            if sc >= MIN_BLAST and sc > best["score"]:
                best["score"] = sc
                best["assignment"] = dict(assignment)
            return

        for pos in candidates:
            if pos in assignment.values():
                continue
            assignment[var_idx] = pos
            bt(var_idx + 1, assignment)
            del assignment[var_idx]

    bt(0, {})
    return best["assignment"]