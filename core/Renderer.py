                  
                                           
                                                    

import tkinter as tk
from core.Game import (WALL, PLAYER, BOX, GOAL,
                       BOX_ON_GOAL, PLAYER_ON_GOAL, PLAYER2,
                       PLAYER2_ON_GOAL, EMPTY)

                              
BOMB      = 10
BOMB_GOAL = 11
EXPLODED  = 12

                                                                
THEME = {
    "bg":        "#1a1a2e",
    "panel":     "#16213e",
    "border":    "#3b424b",
    "header":    "#0f3460",
    "accent":     "#8892a4",
    "gold":      "#de9800",
    "green":     "#4ecca3",
    "purple":    "#8b7cf8",
    "blue":      "#5aa9ff",
    "text":      "#f2f4f8",
    "dim":       "#8892a4",
    "wall_fill": "#d07136",
    "wall_b":    "#704002",
    "floor":     "#f9d898",
    "goal_bg":   "#015A17",
    "fog":       "#e2c073",
    "text_black" : "#0f1115",
}


TILE_BG = {
    WALL:          "#e17f3e",
    EMPTY:         "#B8A789",
    GOAL:          "#0d2618",
    PLAYER:        "#115A32",
    PLAYER_ON_GOAL:"#38b08a",
    BOX:           "#9a710a",
    BOX_ON_GOAL:   "#009C1A",
    PLAYER2:       "#7f3fbf",
    PLAYER2_ON_GOAL:"#a08be0",
    BOMB:          "#2a1a3e",
    BOMB_GOAL:     "#4a0a0a",
    EXPLODED:      "#ff6600",
}

CELL = 56                                                  


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

                if val in (GOAL, PLAYER_ON_GOAL, BOX_ON_GOAL, PLAYER2_ON_GOAL):
                    self._draw_goal(cx, cy, sz)
                    if val == GOAL:
                        self.create_text(cx, cy, text="◎",
                            font=("Arial", int(sz * 0.40)),
                            fill=THEME["green"])

                if val in (BOX, BOX_ON_GOAL):
                    self._draw_box(x1, y1, x2, y2, cx, cy, sz,
                                   on_goal=(val == BOX_ON_GOAL))

                if val in (PLAYER, PLAYER_ON_GOAL, PLAYER2, PLAYER2_ON_GOAL):
                    self._draw_player(cx, cy, sz, player=val)

                if val in (BOMB, BOMB_GOAL):
                    self._draw_bomb(cx, cy, sz, activated=(val == BOMB_GOAL))

                if val == EXPLODED:
                    self._draw_exploded(x1, y1, x2, y2, cx, cy, sz)

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

                                                                

    def _draw_wall(self, x1, y1, x2, y2, sz):
        step = sz // 4
        for gy in range(y1 + step, y2, step):
            shift = sz // 8 if ((gy - y1) // step) % 2 == 0 else 0
            for gx in range(x1 + shift, x2, step * 2):
                gx2 = min(gx + step * 2 - 2, x2 - 1)
                gy2 = min(gy + step - 2,      y2 - 1)
                if gx2 > gx and gy2 > gy:
                    self.create_rectangle(gx + 1, gy + 1, gx2, gy2,
                        fill="#663300", outline=THEME["wall_b"], width=0)

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

    def _draw_player(self, cx, cy, sz, player=PLAYER):
        h = sz // 7
        color = "#115A32" if player in (PLAYER, PLAYER_ON_GOAL) else "#7f3fbf"
        hat_color = "#f1c40f" if player in (PLAYER, PLAYER_ON_GOAL) else "#d57eff"

             
        self.create_oval(
            cx - h, cy - sz // 3,
            cx + h, cy - sz // 8,
            fill="#ffd6a5",
            outline="#b9855a",
            width=2
        )

            
        self.create_arc(
            cx - h - 2, cy - sz // 3 - 2,
            cx + h + 2, cy - sz // 8,
            start=0, extent=180,
            fill=hat_color,
            outline="#b67b00",
            width=2
        )

              
        self.create_rectangle(
            cx - h, cy - sz // 9,
            cx + h, cy + sz // 4,
            fill=THEME["blue"],
            outline="#2f72b7",
            width=2
        )

             
        self.create_line(
            cx - h, cy,
            cx - h - sz // 10, cy + sz // 12,
            fill=THEME["green"],
            width=3
        )
        self.create_line(
            cx + h, cy,
            cx + h + sz // 10, cy + sz // 12,
            fill=THEME["green"],
            width=3
        )

              
        self.create_line(
            cx - h // 2, cy + sz // 4,
            cx - h // 2, cy + sz // 2 - 2,
            fill=THEME["border"],
            width=3
        )
        self.create_line(
            cx + h // 2, cy + sz // 4,
            cx + h // 2, cy + sz // 2 - 2,
            fill=THEME["border"],
            width=3
        )

             
        eye = max(2, sz // 20)
        self.create_oval(
            cx - sz // 10 - eye, cy - sz // 4,
            cx - sz // 10 + eye, cy - sz // 4 + eye * 2,
            fill="white", outline=""
        )
        self.create_oval(
            cx + sz // 10 - eye, cy - sz // 4,
            cx + sz // 10 + eye, cy - sz // 4 + eye * 2,
            fill="white", outline=""
        )

                 
        self.create_oval(
            cx - sz // 10 - 1, cy - sz // 4 + 1,
            cx - sz // 10 + 1, cy - sz // 4 + 3,
            fill="black", outline=""
        )
        self.create_oval(
            cx + sz // 10 - 1, cy - sz // 4 + 1,
            cx + sz // 10 + 1, cy - sz // 4 + 3,
            fill="black", outline=""
        )
        
    def _draw_bomb(self, cx, cy, sz, activated=False):
        """Vẽ trái Bom (bom)."""
        r = sz // 3
                  
        color = "#cc2200" if activated else "#9b59b6"
        outline = "#ff4444" if activated else "#6c3483"
        self.create_oval(cx - r, cy - r + 4, cx + r, cy + r + 4,
            fill=color, outline=outline, width=2)
                  
        fuse_col = "#f39c12" if activated else "#95a5a6"
        self.create_line(cx, cy - r + 4, cx + r // 2, cy - r - 4,
            fill=fuse_col, width=2)
                 
        self.create_text(cx, cy + 4, text="💣" if activated else "🔴",
            font=("Arial", int(sz * 0.30)))

    def _draw_exploded(self, x1, y1, x2, y2, cx, cy, sz):
        """Vẽ ô tường bị phá (hiệu ứng nổ)."""
        import random
        colors = ["#ff6600", "#ffaa00", "#ff2200", "#ffff00"]
        for _ in range(6):
            rx1 = x1 + random.randint(2, sz // 3)
            ry1 = y1 + random.randint(2, sz // 3)
            rx2 = rx1 + random.randint(4, 12)
            ry2 = ry1 + random.randint(4, 12)
            self.create_rectangle(rx1, ry1, min(rx2, x2-2), min(ry2, y2-2),
                fill=random.choice(colors), outline="", width=0)
        self.create_text(cx, cy, text="💥",
            font=("Arial", int(sz * 0.40)))
