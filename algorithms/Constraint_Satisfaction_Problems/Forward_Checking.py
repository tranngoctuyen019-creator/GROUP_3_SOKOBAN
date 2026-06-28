from algorithms.Constraint_Satisfaction_Problems.Helpers import (
    blast_cells, interior_walls, floor_cells,
    score_position, NUM_BOMBS, MIN_BLAST,
)

def forward_checking(domains, var, value, unassigned):
    removed = {}
    for other in unassigned:
        if other == var:
            continue
        if value in domains[other]:
            domains[other].remove(value)
            removed.setdefault(other, []).append(value)
        if not domains[other]: 
            return None
    return removed                

def forward_check(assignment, domains, candidates, target_walls, grid, best):
    if len(assignment) == NUM_BOMBS:
        covered = set()
        for pos in assignment.values():
            covered |= (blast_cells(*pos, grid) & target_walls)
        sc = len(covered)
        if sc >= MIN_BLAST and sc > best["score"]:
            best["score"] = sc
            best["assignment"] = dict(assignment)
        return

    unassigned = [i for i in range(NUM_BOMBS) if i not in assignment]
    var = min(unassigned, key=lambda i: len(domains[i]))

    for value in list(domains[var]):
        if value in assignment.values():
            continue

        assignment[var] = value
        removed = forward_checking(domains, var, value, unassigned)

        if removed is not None:
            forward_check(assignment, domains, candidates, target_walls, grid, best)

            for other, vals in removed.items():
                for v in vals:
                    if v not in domains[other]:
                        domains[other].append(v)

        del assignment[var]

def solve_forward_checking(grid):
    candidates = floor_cells(grid)
    target_walls = interior_walls(grid)

    if len(candidates) < NUM_BOMBS: return None

    candidates.sort(key=lambda p: -score_position(p, grid, target_walls))
    domains = {i: list(candidates) for i in range(NUM_BOMBS)}
    best = {"assignment": None, "score": -1}

    forward_check({}, domains, candidates, target_walls, grid, best)
    return best["assignment"]