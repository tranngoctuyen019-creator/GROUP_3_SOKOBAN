# core/renderer.py
# MapCanvas dùng chung cho tất cả panel GUI
# Chỉ chịu trách nhiệm VẼ, không có logic thuật toán

import tkinter as tk
from core.Game import (WALL, PLAYER, BOX, GOAL,
                       BOX_ON_GOAL, PLAYER_ON_GOAL, EMPTY)

# ── Màu sắc giao diện ─────────────────────────────────────────
THEME = {
    "bg":        "#1a1a2e",
    "panel":     "#16213e",
    "border":    "#3b424b",
    "header":    "#0f3460",
    "accent":     "#8892a4",
    "gold":      "#f5a623",
    "green":     "#4ecca3",
    "purple":    "#8b7cf8",
    "blue":      "#5aa9ff",
    "text":      "#f2f4f8",
    "dim":       "#8892a4",
    "wall_fill": "#2d3561",
    "wall_b":    "#12152a",
    "floor":     "#1e2a45",
    "goal_bg":   "#164c36",
    "fog":       "#0f1115",
    "text_black" : "#0f1115",
}


TILE_BG = {
    WALL:           "#2d3561",
    EMPTY:          "#161e31",
    GOAL:           "#0d2618",
    PLAYER:         "#115A32",
    PLAYER_ON_GOAL:  "#38b08a",
    BOX:            "#c47d0e",
    BOX_ON_GOAL:     "#01DE26",
}

CELL = 56   # pixel mỗi ô — thay đổi ở đây để scale toàn bộ


class MapCanvas(tk.Canvas):
    """
    Canvas vẽ bản đồ Sokoban.

    Tham số:
        parent      : widget cha
        grid        : 2D list trạng thái ban đầu
        cell_size   : kích thước ô pixel (mặc định CELL)
        fog_cells   : set of (r,c) bị che khuất (dùng cho belief state)
    """

    def __init__(self, parent, grid, cell_size=CELL, fog_cells=None, **kw):
        rows, cols = len(grid), len(grid[0])
        super().__init__(
            parent,
            width=cols * cell_size,
            height=rows * cell_size,
            bg=THEME["bg"],
            highlightthickness=0,
            **kw
        )
        self.cell_size = cell_size
        self.draw(grid, fog_cells)

    # ── API công khai ──────────────────────────────────────────

    def draw(self, grid, fog_cells=None):
        """Vẽ lại toàn bộ bản đồ."""
        self.delete("all")
        fog = fog_cells or set()
        sz  = self.cell_size

        for r, row in enumerate(grid):
            for c, val in enumerate(row):
                x1, y1 = c * sz, r * sz
                x2, y2 = x1 + sz, y1 + sz
                cx, cy  = x1 + sz // 2, y1 + sz // 2

                # Ô bị che (fog of war)
                if (r, c) in fog:
                    self.create_rectangle(x1, y1, x2, y2,
                        fill=THEME["fog"], outline=THEME["border"], width=1)
                    self.create_text(cx, cy, text="?",
                        font=("Consolas", int(sz * 0.3)),
                        fill="#1a2030")
                    continue

                bg = TILE_BG.get(val, THEME["floor"])
                self.create_rectangle(x1, y1, x2, y2,
                    fill=bg, outline=THEME["border"], width=1)

                if val == WALL:
                    self._draw_wall(x1, y1, x2, y2, sz)
                    continue

                if val in (GOAL, PLAYER_ON_GOAL, BOX_ON_GOAL):
                    self._draw_goal(cx, cy, sz)
                    if val == GOAL:
                        self.create_text(cx, cy, text="◎",
                            font=("Arial", int(sz * 0.40)),
                            fill=THEME["green"])

                if val in (BOX, BOX_ON_GOAL):
                    self._draw_box(x1, y1, x2, y2, cx, cy, sz,
                                   on_goal=(val == BOX_ON_GOAL))

                if val in (PLAYER, PLAYER_ON_GOAL):
                    self._draw_player(cx, cy, sz)

    def draw_belief(self, grid, visible_cells):
        """
        Vẽ bản đồ với fog of war.
        visible_cells: set of (r,c) mà agent nhìn thấy được.
        """
        all_cells = {(r, c)
                     for r in range(len(grid))
                     for c in range(len(grid[0]))}
        fog = all_cells - visible_cells
        self.draw(grid, fog_cells=fog)

    # ── Vẽ từng loại ô ────────────────────────────────────────

    def _draw_wall(self, x1, y1, x2, y2, sz):
        step = sz // 4
        for gy in range(y1 + step, y2, step):
            shift = sz // 8 if ((gy - y1) // step) % 2 == 0 else 0
            for gx in range(x1 + shift, x2, step * 2):
                gx2 = min(gx + step * 2 - 2, x2 - 1)
                gy2 = min(gy + step - 2,      y2 - 1)
                if gx2 > gx and gy2 > gy:
                    self.create_rectangle(gx + 1, gy + 1, gx2, gy2,
                        fill="#1B2A3D", outline=THEME["wall_b"], width=0)

    def _draw_goal(self, cx, cy, sz):
        m = sz // 3
        self.create_oval(cx - m, cy - m, cx + m, cy + m,
            fill=THEME["goal_bg"], outline=THEME["green"], width=2)

    def _draw_box(self, x1, y1, x2, y2, cx, cy, sz, on_goal=False):
        color = THEME["accent"] if on_goal else THEME["gold"]
        m = sz // 5
        self.create_rectangle(x1 + m, y1 + m, x2 - m, y2 - m,
            fill=color, outline=THEME["bg"], width=2)
        self.create_rectangle(x1 + m + 3, y1 + m + 3,
                               x2 - m - 3, y2 - m - 3,
            fill="", outline="white", width=1)
        sym = "✓" if on_goal else "■"
        self.create_text(cx, cy, text=sym,
            font=("Arial", int(sz * 0.28), "bold"),
            fill=THEME["bg"])

    def _draw_player(self, cx, cy, sz):
        h = sz // 7
        # đầu
        self.create_oval(cx - h, cy - sz // 3, cx + h, cy - sz // 8,
            fill=THEME["green"], outline="#2a8a6a", width=1)
        # thân
        self.create_rectangle(cx - h, cy - sz // 9,
                               cx + h, cy + sz // 4,
            fill=THEME["green"], outline="#2a8a6a", width=1)
        # mắt
        self.create_oval(cx - sz//9, cy - sz//4,
                         cx - sz//18, cy - sz//6, fill=THEME["bg"])
        self.create_oval(cx + sz//18, cy - sz//4,
                         cx + sz//9,  cy - sz//6, fill=THEME["bg"])
