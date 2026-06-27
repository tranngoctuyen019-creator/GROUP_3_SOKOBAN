# core/maps.py
# Định nghĩa tất cả map dùng chung
# Thêm map mới vào dict MAPS là đủ, không cần sửa file khác

# Ký hiệu: 0=sàn 1=tường 2=người 3=thùng 4=đích 5=thùng+đích 6=người+đích

MAPS = {
    # ── MAP 1: 2 thùng 2 đích – ít chướng ngại ────────────────
    "map1": {
        "name":  "Map 1",
        "desc":  "2 thùng · 2 đích · ít vật cản",
        "boxes": 2,
        "grid": [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 3, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 4, 0, 1],
            [1, 0, 2, 0, 3, 0, 0, 1],
            [1, 0, 0, 0, 0, 4, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ],
    },

    # ── MAP 2: 2 thùng 2 đích – nhiều chướng ngại ─────────────
    "map2": {
        "name":  "Map 2",
        "desc":  "2 thùng · 2 đích · nhiều vật cản",
        "boxes": 2,
        "grid": [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 0, 3, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 4, 1],
            [1, 0, 2, 0, 3, 1, 0, 1],
            [1, 0, 0, 1, 0, 0, 4, 1],
            [1, 0, 0, 0, 1, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ],
    },

    # ── MAP 3: 3 thùng 3 đích ──────────────────────────────────
    "map3": {
        "name":  "Map 3",
        "desc":  "3 thùng · 3 đích",
        "boxes": 3,
        "grid": [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 4, 1],
            [1, 0, 1, 3, 0, 1, 0, 1],
            [1, 4, 0, 0, 0, 0, 0, 1],
            [1, 0, 3, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 3, 0, 4, 1],
            [1, 0, 2, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ],
    },

    # ── MAP ĐỐI KHÁNG (Adversarial) ────────────────────────────
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
