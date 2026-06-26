# core/maps.py
# Định nghĩa tất cả map dùng chung
# Thêm map mới vào dict MAPS là đủ, không cần sửa file khác

# Ký hiệu: 0=sàn 1=tường 2=người 3=thùng 4=đích 5=thùng+đích 6=người+đích

MAPS = {
    # ── MAP THƯỜNG (Uninformed / Informed / Local / CSP) ────────
    "easy": {
        "name":  "Map Dễ",
        "desc":  "1 thùng · 2 vật cản",
        "boxes": 1,
        "grid": [
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 3, 0, 0, 1],
            [1, 0, 0, 0, 1, 4, 1],
            [1, 0, 2, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1],
        ],
    },
    "hard": {
        "name":  "Map Khó",
        "desc":  "2 thùng · 3 vật cản",
        "boxes": 2,
        "grid": [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 3, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 4, 1],
            [1, 0, 2, 0, 3, 1, 0, 1],
            [1, 0, 0, 1, 0, 0, 4, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ],
    },

    # ── MAP ĐỐI KHÁNG (Adversarial) ────────────────────────────
    # Người 1 (trái): thùng=3, đích=4
    # Người 2 (phải): thùng=7, đích=8  (xử lý riêng trong adversarial.py)
    "adversarial": {
        "name":  "Map Đối Kháng",
        "desc":  "2 người chơi · mỗi người 1 thùng",
        "boxes": 2,
        "grid": [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 0, 3, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
            [1, 4, 0, 0, 1, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 1, 0, 0, 8, 1],
            [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 7, 0, 0, 6, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ],
        # 6=người2, 7=thùng người2, 8=đích người2
    },

    # ── MAP BELIEF STATE (Partial Observation) ──────────────────
    "belief": {
        "name":  "Map Belief State",
        "desc":  "Tầm nhìn giới hạn bán kính 2 ô",
        "boxes": 1,
        "grid": [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 3, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1],
            [1, 2, 0, 1, 0, 0, 4, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ],
        "vision_radius": 2,
    },
}

def get_map(map_id):
    """Trả về deep copy của map để tránh modify map gốc."""
    import copy
    return copy.deepcopy(MAPS[map_id])

def list_maps():
    return list(MAPS.keys())
