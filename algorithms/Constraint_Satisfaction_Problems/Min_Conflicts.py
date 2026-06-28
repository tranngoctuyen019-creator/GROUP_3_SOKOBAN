import random

from algorithms.Constraint_Satisfaction_Problems.Helpers import (
    blast_cells, interior_walls, floor_cells,
    score_position, NUM_BOMBS, MIN_BLAST,
)


def count_conflicts(var_idx, pos, assignment, grid, target_walls):
    conflicts = sum(
        1 for other, other_pos in assignment.items()
        if other != var_idx and other_pos == pos
    )
    temp = dict(assignment)
    temp[var_idx] = pos
    covered = set()
    for p in temp.values():
        covered |= (blast_cells(*p, grid) & target_walls)
    return conflicts * 100 - len(covered)


def solve_min_conflicts(grid, max_steps: int = 1000):
    candidates = floor_cells(grid)
    target_walls = interior_walls(grid)

    if len(candidates) < NUM_BOMBS:
        return None

    initial_positions = random.sample(candidates, NUM_BOMBS)
    assignment = {i: initial_positions[i] for i in range(NUM_BOMBS)}

    best = {"assignment": None, "score": -1}

    def current_score():
        covered = set()
        for pos in assignment.values():
            covered |= (blast_cells(*pos, grid) & target_walls)
        return len(covered)

    def is_consistent():
        positions = list(assignment.values())
        return len(positions) == len(set(positions)) and current_score() >= MIN_BLAST

    for step in range(max_steps):
        if is_consistent():
            sc = current_score()
            if sc > best["score"]:
                best["score"] = sc
                best["assignment"] = dict(assignment)
            if step > 50:
                break

        conflicted = [
            i for i in range(NUM_BOMBS)
            if any(assignment[j] == assignment[i] for j in range(NUM_BOMBS) if j != i)
        ]
        if not conflicted:
            conflicted = list(range(NUM_BOMBS))

        var = random.choice(conflicted)

        min_conf = None
        best_vals = []
        for pos in candidates:
            c = count_conflicts(var, pos, assignment, grid, target_walls)
            if min_conf is None or c < min_conf:
                min_conf = c
                best_vals = [pos]
            elif c == min_conf:
                best_vals.append(pos)

        assignment[var] = random.choice(best_vals)

        if is_consistent():
            sc = current_score()
            if sc > best["score"]:
                best["score"] = sc
                best["assignment"] = dict(assignment)

    if best["assignment"] is None:
        candidates.sort(key=lambda p: -score_position(p, grid, target_walls))
        used: set = set()
        fallback: dict = {}
        for i in range(NUM_BOMBS):
            for pos in candidates:
                if pos not in used:
                    fallback[i] = pos
                    used.add(pos)
                    break
        best["assignment"] = fallback if len(fallback) == NUM_BOMBS else None

    return best["assignment"]