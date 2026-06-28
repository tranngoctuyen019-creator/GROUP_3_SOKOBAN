# algorithms/belief_state/no_observation.py

import time
from collections import deque
from core.Game import apply_move, is_solved, grid_to_key, find_player, DIRECTIONS, EMPTY, PLAYER
from algorithms._base import make_result, Node

def get_belief_key(grid_set):
    """Băm tập hợp trạng thái để nhận diện trùng lặp toàn cục."""
    return "|".join(sorted(str(grid_to_key(g)) for g in grid_set))

def solve_no_observation(initial_grid):
    """
    Sensorless Search: Xuất phát từ góc TRÊN - TRÁI.
    Giao diện tối hoàn toàn, chỉ sáng những ô nhân vật đã từng bước qua.
    """
    t0 = time.time()
    nodes_visited = 0
   
    # 1. ĐỊNH VỊ GÓC TRÊN TRÁI VÀ KHỞI TẠO MAP
    real_p = find_player(initial_grid)
    base_grid = [list(row) for row in initial_grid]
    if real_p:
        base_grid[real_p[0]][real_p[1]] = EMPTY
       
    R, C = len(base_grid), len(base_grid[0])
    placed = False
   
    for r in range(R):
        for c in range(C):
            if base_grid[r][c] == EMPTY:
                base_grid[r][c] = PLAYER
                placed = True
                break
        if placed:
            break
           
    if not placed and real_p:
        base_grid[real_p[0]][real_p[1]] = PLAYER

    # Tạo node xuất phát
    start_node = Node([base_grid], depth=0)
   
    # Vị trí ban đầu của player
    start_pos = find_player(base_grid)
    start_visited_cells = {start_pos} if start_pos else set()
   
    # Dùng dict để lưu vết ô sáng, tránh lỗi __slots__ của Node
    revealed_paths_map = {id(start_node): start_visited_cells}

    if is_solved(base_grid):
        return make_result([(base_grid, None)], True, 1, 0, time.time() - t0,
                           {"visible_list": [start_visited_cells], "vision_radius": 0})

    queue = deque([start_node])
    visited = {get_belief_key({grid_to_key(base_grid)})}

    max_depth = 0
    while queue:
        current_node = queue.popleft()
        nodes_visited += 1
        max_depth = max(max_depth, current_node.depth)

        if current_node.depth >= 60:
            continue

        for move in DIRECTIONS:
            next_belief_set = set()
           
            for grid in current_node.grid:
                if find_player(grid) is None:
                    next_belief_set.add(grid_to_key(grid))
                    continue
                grid_copy = [list(row) for row in grid]
                new_grid = apply_move(grid_copy, move)
                next_belief_set.add(grid_to_key(new_grid) if new_grid else grid_to_key(grid))
           
            new_key = get_belief_key(next_belief_set)
            if new_key not in visited:
                visited.add(new_key)
               
                child_node = Node([list(g) for g in next_belief_set], parent=current_node, move=move, depth=current_node.depth + 1)
               
                # CẬP NHẬT Ô SÁNG QUA DICT: Lấy tập ô sáng của cha + ô hiện tại của con
                parent_paths = revealed_paths_map.get(id(current_node), set())
                child_paths = set(parent_paths)
               
                current_p = find_player(child_node.grid[0])
                if current_p:
                    child_paths.add(current_p)
               
                # Lưu vào bộ nhớ tạm bằng id của child_node
                revealed_paths_map[id(child_node)] = child_paths

                # KIỂM TRA ĐÍCH
                if all(is_solved(g) for g in child_node.grid):
                    path = []
                    vis_list = []
                    curr = child_node
                   
                    # Tìm tọa độ của tất cả các ô đích để làm hiệu ứng sáng cuối game
                    from core.Game import find_goals
                    all_goals = set(find_goals(child_node.grid[0]))
                   
                    is_final_step = True # Đánh dấu bước cuối cùng (vị trí chiến thắng)
                   
                    while curr and curr.move is not None:
                        path.append((curr.grid[0], curr.move))
                       
                        # Lấy danh sách các ô đã đi qua của node hiện tại
                        current_step_paths = set(revealed_paths_map.get(id(curr), set()))
                       
                        # Nếu là bước cuối cùng (đích), cộng thêm tọa độ các ô đích vào cho nó sáng bừng lên
                        if is_final_step:
                            current_step_paths.update(all_goals)
                            is_final_step = False # Các bước trước đó thì không cho sáng đích
                           
                        vis_list.append(current_step_paths)
                        curr = curr.parent
                       
                    if curr:
                        path.append((curr.grid[0], None))
                        vis_list.append(revealed_paths_map.get(id(curr), set()))
                       
                    path.reverse()
                    vis_list.reverse()
                   
                    return make_result(path, True, nodes_visited, child_node.depth, time.time() - t0,
                                       {"visible_list": vis_list, "vision_radius": 0})
                   
                queue.append(child_node)

    return make_result([], False, nodes_visited, max_depth, time.time() - t0, {"vision_radius": 0})