from algorithms.Constraint_Satisfaction_Problems.Helpers import (
    blast_cells, interior_walls, floor_cells,
    score_position, NUM_BOMBS, MIN_BLAST,
)


def solve_backtracking(grid):
    candidates = floor_cells(grid)
    target_walls = interior_walls(grid)

    if len(candidates) < NUM_BOMBS:
        return None
    candidates.sort(
        key=lambda p: -score_position(p, grid, target_walls)
    )
    best = {
        "assignment": None,
        "score": -1,
    }

    def recursive_backtracking(assignment):
        if len(assignment) == NUM_BOMBS:
            covered = set()
            for pos in assignment.values():
                covered |= (
                    blast_cells(*pos, grid)
                    & target_walls
                )

            score = len(covered)
            if score >= MIN_BLAST and score > best["score"]:
                best["score"] = score
                best["assignment"] = assignment.copy()
            return

        var = len(assignment)
        for value in candidates:
            if value in assignment.values():
                continue
            assignment[var] = value
            result = recursive_backtracking(assignment)
            if result is not None:
                return result

            del assignment[var]
        return None
    
    recursive_backtracking({})
    return best["assignment"]