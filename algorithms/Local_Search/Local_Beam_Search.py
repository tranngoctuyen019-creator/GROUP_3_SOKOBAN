import time
from core.Game import apply_move, is_solved, grid_to_key, heuristic, extract_path, DIRECTIONS
from algorithms._base import Node, make_result

def solve_local_beam_search(initial_grid, k=10, max_steps=1000):
    """
    Local Beam Search tối ưu
    """
    t0 = time.time()
    nodes = 0
    depth = 0

    start_node = Node(initial_grid, cost=0)
    beams = [start_node]
    
    # Chỉ ghi nhận trạng thái đã thực sự được DUYỆT trong chùm
    visited = {grid_to_key(initial_grid)}

    for step in range(max_steps):
        if not beams:
            break
            
        # Kiểm tra đích
        for node in beams:
            nodes += 1
            if is_solved(node.grid):
                return make_result(extract_path(node), True, nodes, depth, time.time() - t0, {"beams": k})

        # Sinh tập ứng viên
        candidates = []
        for node in beams:
            for move in DIRECTIONS:
                ng = apply_move(node.grid, move)
                if ng is None:
                    continue
                
                key = grid_to_key(ng)
                # KHÔNG gán visited ở đây để giữ cơ hội so sánh Heuristic toàn cục
                if key not in visited:
                    child = Node(ng, parent=node, move=move, depth=node.depth + 1)
                    candidates.append((heuristic(ng), child, key))

        if not candidates:
            break

        # Sắp xếp ứng viên theo Heuristic tốt nhất
        candidates.sort(key=lambda x: x[0])

        # Chọn lọc k phần tử tốt nhất và KHÔNG TRÙNG NHAU vào chùm mới
        beams = []
        seen_this_step = set()
        
        for h_val, child_node, key in candidates:
            if key not in visited and key not in seen_this_step:
                seen_this_step.add(key)
                visited.add(key) # Chỉ khi lọt vào Top K mới chính thức khóa key
                beams.append(child_node)
                
                if len(beams) == k:
                    break
                    
        depth = max(depth, step + 1)

    # Nếu chạy hết bước mà chưa xong, trả về thằng có Heuristic tốt nhất hiện tại
    if beams:
        best_node = min(beams, key=lambda n: heuristic(n.grid))
        return make_result(extract_path(best_node), is_solved(best_node.grid), nodes, depth, 
                           time.time() - t0, {"beams": k})
                           
    return make_result([], False, nodes, depth, time.time() - t0)