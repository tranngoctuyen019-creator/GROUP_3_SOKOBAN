import time
from core.Game import apply_move, is_solved, grid_to_key, DIRECTIONS, has_deadlock, heuristic
from algorithms._base import make_result

TIME_LIMIT = 30.0
NODE_LIMIT = 150_000

OPPOSITE = {
    "UP":    "DOWN",
    "DOWN":  "UP",
    "LEFT":  "RIGHT",
    "RIGHT": "LEFT",
}

#Sắp xếp theo heuristic tăng dần.
def sorted_actions(grid):
    scored = []
    for move in DIRECTIONS:       
        next_g = apply_move(grid, move)
        if next_g is None:
            score = float('inf')
        else:
            score = heuristic(next_g) 
        scored.append((move, score))
    scored.sort(key=lambda x: x[1])
    return [m for m, _ in scored]

"""
 Trả về (and1_grid, and2_grid) tương ứng với:
      - and1_grid : kết quả của đúng action (AND node 1)
      - and2_grid : kết quả trượt – 1 trong 3 hướng còn lại
"""
def get_all_results(grid, action):
    and1_grid = apply_move(grid, action)
    if and1_grid is None or has_deadlock(and1_grid):
        return None, None   # action không hợp lệ

    exclude = OPPOSITE.get(action)
    and2_grid = None

    for move in DIRECTIONS:
        if move == action:
            continue        
        if move == exclude:
            continue     
        result = apply_move(grid, move)
        if result is None:
            continue
        if grid_to_key(result) == grid_to_key(grid):
            continue  
        if has_deadlock(result):
            continue
        and2_grid = result 
        break

    return and1_grid, and2_grid

# AND-OR Graph Search cho môi trường không xác định (Sokoban có trượt)
def solve_and_or(initial_grid, max_depth=150):
    t0 = time.time()
    nodes = [0]
    timed_out = [False]
    best_path = [[(initial_grid, None)]]

    def or_search(grid, path, path_list):
        nodes[0] += 1

        if len(path_list) > len(best_path[0]):
            best_path[0] = list(path_list)

        if nodes[0] >= NODE_LIMIT or (time.time() - t0) >= TIME_LIMIT:
            timed_out[0] = True
            return None

        if is_solved(grid):
            return []                          

        key = grid_to_key(grid)
        if key in path: return None                  
        if len(path) >= max_depth: return None
        new_path = path | {key}

        # Duyệt từng action theo heuristic
        for move in sorted_actions(grid):    
            if timed_out[0]: return None
            and1_grid, and2_grid = get_all_results(grid, move)
            if and1_grid is None: continue   

            #AND1 luôn có; AND2 thêm vào nếu tồn tại
            result_states = [and1_grid]
            if and2_grid is not None:
                result_states.append(and2_grid)

            next_path_list = path_list + [(and1_grid, move)]

            plan = and_search(result_states, new_path, next_path_list)
            if plan is not None: return [move, plan]           

        return None                            

    def and_search(states, path, path_list):
        plans = {}
        for state in states:
            plan_s = or_search(state, path, path_list)
            if plan_s is None:
                return None                  
            plans[grid_to_key(state)] = (state, plan_s)
        return plans

    raw_plan = or_search(initial_grid, set(), [(initial_grid, None)])
    found = raw_plan is not None

    def flatten_plan(grid, plan):
        result = [(grid, None)]
        if not plan:
            return result
        action, mapping = plan
        for k, (next_grid, sub_plan) in mapping.items():
            result[-1] = (grid, action)
            result.extend(flatten_plan(next_grid, sub_plan))
            break
        return result

    def collect_solution_branches(grid, plan, depth=0):
        branches = []
        if not plan or depth > 30: return branches

        action, mapping = plan
        states_in_plan = list(mapping.values()) 
        and1_grid = states_in_plan[0][0] if states_in_plan else None
        and2_grid = states_in_plan[1][0] if len(states_in_plan) > 1 else None
        branches.append((grid, and1_grid, and2_grid, action))

        if states_in_plan:
            ng, sp = states_in_plan[0]
            if sp:
                branches.extend(collect_solution_branches(ng, sp, depth + 1))

        return branches

    if found:
        path_list = flatten_plan(initial_grid, raw_plan)
        and_branches = collect_solution_branches(initial_grid, raw_plan)
    else:
        path_list = best_path[0]
        and_branches = []
        for i in range(len(path_list) - 1):
            or_grid, _ = path_list[i]
            and1_grid, action = path_list[i + 1]
            and2_grid = None
            if and1_grid is not None and action is not None:
                _, and2_grid = get_all_results(or_grid, action)
            and_branches.append((or_grid, and1_grid, and2_grid, action))

    result = make_result(path_list, found, nodes[0], max_depth, time.time() - t0)
    result["and_branches"] = and_branches
    result["timed_out"] = timed_out[0]
    return result
