from algorithms.Constraint_Satisfaction_Problems.Helpers import (
    blast_cells, interior_walls, floor_cells,
    score_position, NUM_BOMBS, MIN_BLAST,
)


def solve_forward_checking(grid):
    """
    Backtracking + forward checking with MRV heuristic.
    After each assignment, shrink the domains of unassigned variables
    and prune branches where a domain becomes empty.
    """
    candidates = floor_cells(grid)
    target_walls = interior_walls(grid)

    if len(candidates) < NUM_BOMBS:
        return None

    candidates.sort(key=lambda p: -score_position(p, grid, target_walls))

    domains = {i: list(candidates) for i in range(NUM_BOMBS)}

    best = {"assignment": None, "score": -1}

    def fc(var_idx, assignment):
        if var_idx == NUM_BOMBS:
            covered = set()
            for pos in assignment.values():
                covered |= (blast_cells(*pos, grid) & target_walls)
            sc = len(covered)
            if sc >= MIN_BLAST and sc > best["score"]:
                best["score"] = sc
                best["assignment"] = dict(assignment)
            return

        unassigned = [i for i in range(NUM_BOMBS) if i not in assignment]
        # MRV: pick variable with smallest remaining domain
        var = min(unassigned, key=lambda i: len(domains[i]))

        for pos in list(domains[var]):
            if pos in assignment.values():
                continue

            assignment[var] = pos

            # Forward check: remove pos from peers' domains
            removed = {}
            failure = False
            for other in unassigned:
                if other == var:
                    continue
                if pos in domains[other]:
                    domains[other].remove(pos)
                    removed.setdefault(other, []).append(pos)
                if not domains[other]:
                    failure = True
                    break

            if not failure:
                fc(var_idx + 1, assignment)

            # Restore pruned values
            for other, vals in removed.items():
                for v in vals:
                    if v not in domains[other]:
                        domains[other].append(v)

            del assignment[var]

    fc(0, {})
    return best["assignment"]