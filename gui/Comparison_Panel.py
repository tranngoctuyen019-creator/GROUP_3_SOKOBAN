# gui/comparison_panel.py
# Thanh so sánh nhỏ hiển thị dưới mỗi nhóm thuật toán

import tkinter as tk
from core.Renderer import THEME

BAR_MAX = 320   # pixel chiều rộng tối đa của bar


class ComparisonBar(tk.Frame):
    """
    Hiển thị bảng so sánh 3 thuật toán:
    - Thanh bar tỉ lệ: node duyệt, bước giải, thời gian
    - Số liệu chính xác bên cạnh
    """

    METRICS = [
        ("nodes_visited", "Node duyệt", THEME["purple"]),
        ("solution_len",  "Số bước",    THEME["gold"]),
        ("time_elapsed",  "Thời gian",  THEME["blue"]),
    ]

    def __init__(self, parent, algo_list, accent_color, **kw):
        super().__init__(parent, bg=THEME["panel"], padx=12, pady=8, **kw)
        self.algo_names = [name for name, _ in algo_list]
        self.accent     = accent_color
        self.bars       = {}   # (algo_name, metric) -> Frame fill
        self.lbls       = {}   # (algo_name, metric) -> Label value
        self._build()

    def _build(self):
        tk.Label(self, text="📊  SO SÁNH",
            font=("Consolas", 8, "bold"),
            fg=THEME["dim"], bg=THEME["panel"]).grid(
            row=0, column=0, sticky="w", pady=(0, 4))

        # Header cột
        for j, (_, metric_name, color) in enumerate(self.METRICS):
            tk.Label(self, text=metric_name,
                font=("Consolas", 8, "bold"),
                fg=color, bg=THEME["panel"]).grid(
                row=0, column=j + 1, padx=10, sticky="w")

        for i, algo_name in enumerate(self.algo_names):
            tk.Label(self, text=algo_name,
                font=("Consolas", 9, "bold"),
                fg=self.accent, bg=THEME["panel"]).grid(
                row=i + 1, column=0, padx=(0, 12), sticky="w", pady=2)

            for j, (key, _, color) in enumerate(self.METRICS):
                cell = tk.Frame(self, bg=THEME["panel"])
                cell.grid(row=i + 1, column=j + 1, padx=10, sticky="ew", pady=2)

                bg_bar = tk.Frame(cell, bg=THEME["border"],
                                  height=12, width=BAR_MAX)
                bg_bar.pack(side="left")
                bg_bar.pack_propagate(False)

                fill = tk.Frame(bg_bar, bg=color, height=12)
                fill.place(x=0, y=0, width=0, height=12)
                self.bars[(algo_name, key)] = fill

                lbl = tk.Label(cell, text="–",
                    font=("Consolas", 8),
                    fg=color, bg=THEME["panel"], width=10)
                lbl.pack(side="left", padx=4)
                self.lbls[(algo_name, key)] = lbl

        self.lbl_remark = tk.Label(self, text="",
            font=("Consolas", 8, "italic"),
            fg=THEME["gold"], bg=THEME["panel"])
        self.lbl_remark.grid(row=len(self.algo_names) + 1,
                             column=0, columnspan=4,
                             sticky="w", pady=(6, 0))

    def update(self, results):
        """
        results: list of dict (cùng thứ tự algo_names),
                 phần tử None nếu chưa giải.
        """
        for key, _, _ in self.METRICS:
            vals = []
            for r in results:
                v = r.get(key, 0) if r else 0
                vals.append(v if v else 0)

            max_v = max(vals) if max(vals) > 0 else 1

            for i, (algo_name, v) in enumerate(zip(self.algo_names, vals)):
                fill = self.bars[(algo_name, key)]
                lbl  = self.lbls[(algo_name, key)]
                width = int(v / max_v * BAR_MAX)
                fill.place(width=width)

                if v == 0:
                    lbl.config(text="–")
                elif key == "time_elapsed":
                    lbl.config(text=f"{v:.4f}s")
                else:
                    lbl.config(text=f"{v:,}")

        # Nhận xét tự động
        valid = [(i, r) for i, r in enumerate(results) if r and r.get("found")]
        if len(valid) == 3:
            # So sánh node duyệt
            node_vals = [(r["nodes_visited"], self.algo_names[i]) for i, r in valid]
            node_vals.sort()
            best  = node_vals[0][1]
            worst = node_vals[-1][1]
            ratio = node_vals[-1][0] / max(node_vals[0][0], 1)
            self.lbl_remark.config(
                text=f"→ {best} hiệu quả nhất · "
                     f"{worst} duyệt gấp {ratio:.1f}× node hơn")
        elif len(valid) > 0:
            self.lbl_remark.config(text="→ Giải tất cả để xem so sánh đầy đủ")
        else:
            self.lbl_remark.config(text="")
