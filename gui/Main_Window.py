# gui/main_window.py

import tkinter as tk
from tkinter import ttk
import copy

from core.Renderer import MapCanvas, THEME, CELL
from core.Game import find_player, DIRECTIONS

from algorithms.Uninformed_Search   import BFS, DFS, IDS
from algorithms.Informed_Search     import Greedy, IDA, A
from algorithms.Local_Search        import Simple_Hill, Simulated_Annealing, Local_Beam
from algorithms.Constraint_Satisfaction_Problems          import Backtracking_Search, Forward_Checking, Min_Conflicts
from algorithms.Adversarial_Search      import Minimax, Alpha_Beta, Expectimax
from algorithms.Complex_Environments    import Partial_Observation, And_Or_Search, Sensorless

MAP_OPTIONS = [
    {
        "label": "Map 1 – Dễ (1 thùng)",
        "grid": [
            [1,1,1,1,1,1,1],
            [1,0,0,0,0,0,1],
            [1,0,1,3,0,0,1],
            [1,0,0,0,1,4,1],
            [1,0,2,0,0,0,1],
            [1,0,0,1,0,0,1],
            [1,1,1,1,1,1,1],
        ],
    },
    {
        "label": "Map 2 – Khó (2 thùng)",
        "grid": [
            [1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,3,0,1,0,1],
            [1,0,0,0,0,0,4,1],
            [1,0,2,0,3,1,0,1],
            [1,0,0,1,0,0,4,1],
            [1,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1],
        ],
    },
]

ALGO_GROUPS = [
    {"name": "Uninformed Search", "color": "#4ecca3",
     "algos": [("BFS", BFS()), ("DFS", DFS()), ("IDS", IDS())]},
    {"name": "Informed Search",   "color": "#74b9ff",
     "algos": [("GBFS", Greedy()), ("A*", A()), ("IDA*", IDA())]},
    {"name": "Local Search",      "color": "#f5a623",
     "algos": [("Hill Climbing", Simple_Hill()),
               ("Simulated Annealing", Simulated_Annealing()),
               ("Local Beam Search", Local_Beam())]},
    {"name": "CSP",               "color": "#a29bfe",
     "algos": [("Backtracking", Backtracking_Search()),
               ("Forward Checking", Forward_Checking()),
               ("Min-Conflicts", Min_Conflicts())]},
    {"name": "Adversarial Search","color": "#e94560",
     "algos": [("Minimax", Minimax()), ("Alpha-Beta", Alpha_Beta()),
               ("Expectimax", Expectimax())]},
    {"name": "Belief State",      "color": "#fd79a8",
     "algos": [("Partial Observation", Partial_Observation()),
               ("AND-OR Graph", And_Or_Search()), ("Sensorless", Sensorless())]},
]

# Canvas cell size — bigger for a larger game board
CELL_SIZE = 68

MOVE_ARROW = {"UP": "↑", "DOWN": "↓", "LEFT": "←", "RIGHT": "→"}
MOVE_LABEL = {"UP": "lên", "DOWN": "xuống", "LEFT": "trái", "RIGHT": "phải"}


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sokoban – AI Solver")
        self.configure(bg=THEME["bg"])
        self.resizable(True, True)
        self.state("zoomed")

        self._map_idx  = 0
        self._grp_idx  = 0
        self._algo_idx = 0
        self._result   = None
        self._step     = 0
        self._playing  = False
        self._speed    = 400

        self._build()
        self._load_map()

    # ─────────────────────────────────────── BUILD ─────────────

    def _build(self):
        self._build_header()

        body = tk.Frame(self, bg=THEME["bg"])
        body.pack(fill="both", expand=True, padx=12, pady=(6, 8))

        # 2 columns: left (game), right (info + log)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # ── Left: map selector + canvas + speed + buttons ──
        left = tk.Frame(body, bg=THEME["bg"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.rowconfigure(1, weight=1)  # canvas row expands

        self._build_map_selector(left)

        # Legend + Map nằm ngang
        map_container = tk.Frame(left, bg=THEME["bg"])
        map_container.pack(pady=4)

        legend_frame = tk.Frame(map_container, bg=THEME["bg"])
        legend_frame.pack(side="left", anchor="n", padx=(0, 12))

        canvas_frame = tk.Frame(map_container, bg=THEME["bg"])
        canvas_frame.pack(side="left")

        self._build_legend(legend_frame)
        self._build_canvas_area(canvas_frame)

        self._build_buttons(left)

        # ── Right: top = info+stats, bottom = log ──
        right = tk.Frame(body, bg=THEME["bg"])
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=0)   # info+stats: natural height
        right.rowconfigure(1, weight=1)   # log: expand to fill rest
        right.columnconfigure(0, weight=1)

        top_panel = tk.Frame(right, bg=THEME["panel"], padx=14, pady=10)
        top_panel.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self._build_info_stats(top_panel)
        self._build_speed_control(top_panel)

        log_frame = tk.Frame(right, bg=THEME["panel"], padx=14, pady=10)
        log_frame.grid(row=1, column=0, sticky="nsew")
        self._build_log(log_frame)
        
    # ── Header ──
    def _build_header(self):
        hdr = tk.Frame(self, bg=THEME["header"], pady=10, padx=20)
        hdr.pack(fill="x")

        tk.Label(hdr, text="🎮  SOKOBAN – AI SOLVER",
            font=("Consolas", 14, "bold"),
            fg=THEME["accent"], bg=THEME["header"]).pack(side="left", padx=(0, 24))

        tk.Label(hdr, text="NHÓM THUẬT TOÁN:",
            font=("Consolas", 9, "bold"),
            fg=THEME["dim"], bg=THEME["header"]).pack(side="left", padx=(0, 6))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.TCombobox",
            fieldbackground=THEME["bg"],
            background=THEME["bg"],
            foreground=THEME["text_black"],
            selectbackground=THEME["bg"],
            selectforeground=THEME["accent"],
            arrowcolor=THEME["text"],
            bordercolor=THEME["border"],
            lightcolor=THEME["border"],
            darkcolor=THEME["border"])

        self._grp_var = tk.StringVar()
        self._cb_group = ttk.Combobox(hdr,
            textvariable=self._grp_var,
            values=[g["name"] for g in ALGO_GROUPS],
            state="readonly", font=("Consolas", 9),
            style="Dark.TCombobox", width=22)
        self._cb_group.current(0)
        self._cb_group.pack(side="left", padx=(0, 16))
        self._cb_group.bind("<<ComboboxSelected>>", self._on_group_change)

        tk.Label(hdr, text="THUẬT TOÁN:",
            font=("Consolas", 9, "bold"),
            fg=THEME["dim"], bg=THEME["header"]).pack(side="left", padx=(0, 6))

        self._algo_var = tk.StringVar()
        self._cb_algo = ttk.Combobox(hdr,
            textvariable=self._algo_var,
            state="readonly", font=("Consolas", 9),
            style="Dark.TCombobox", width=22)
        self._cb_algo.pack(side="left", padx=(0, 16))
        self._cb_algo.bind("<<ComboboxSelected>>", self._on_algo_change)
        self._refresh_algo_list()

        tk.Label(hdr,
            text="Uninformed · Informed · Local · CSP · Adversarial · Belief",
            font=("Consolas", 8), fg=THEME["dim"],
            bg=THEME["header"]).pack(side="right", padx=4)

    def _build_map_selector(self, parent):
        row = tk.Frame(parent, bg=THEME["bg"], pady=6)
        row.pack(fill="x")
        tk.Label(row, text="CHỌN MAP",
            font=("Consolas", 8, "bold"),
            fg=THEME["dim"], bg=THEME["bg"]).pack(side="left", padx=(0, 10))
        self._map_var = tk.IntVar(value=0)
        for i, m in enumerate(MAP_OPTIONS):
            tk.Radiobutton(row, text=m["label"],
                variable=self._map_var, value=i,
                command=self._on_map_change,
                font=("Consolas", 9),
                fg=THEME["text"], bg=THEME["bg"],
                selectcolor=THEME["panel"],
                activebackground=THEME["bg"],
                activeforeground=THEME["accent"],
                relief="flat", cursor="hand2").pack(side="left", padx=8)

    def _build_canvas_area(self, parent):
        self._canvas_frame = tk.Frame(parent, bg=THEME["border"], padx=2, pady=2)
        self._canvas_frame.pack(pady=4)
        dummy = MAP_OPTIONS[0]["grid"]
        self._canvas = MapCanvas(self._canvas_frame, dummy, cell_size=CELL_SIZE)
        self._canvas.pack()

    def _build_legend(self, parent):
        leg = tk.Frame(parent, bg=THEME["bg"], pady=3)
        leg.pack(anchor="w", padx=10)
        items = [
            ("■", THEME["gold"],   "Thùng"),
            ("◎", THEME["green"],  "Đích"),
            ("✓", THEME["accent"], "Thùng @ Đích"),
            ("●", THEME["green"],  "Người"),
            ("█", "#2d333b",       "Tường"),
        ]
        for sym, col, lbl in items:
            row = tk.Frame(leg, bg=THEME["bg"])
            row.pack(anchor="w", pady=1)

            tk.Label(
                row,
                text=sym,
                fg=col,
                bg=THEME["bg"],
                font=("Arial", 13, "bold"),
                width=2,
                anchor="w"
            ).pack(side="left")

            tk.Label(
                row,
                text=lbl,
                fg=THEME["dim"],
                bg=THEME["bg"],
                font=("Consolas", 10),
                anchor="w"
            ).pack(side="left")

    # ── Speed control (above solve button) ──
    def _build_speed_control(self, parent):
        outer = tk.Frame(parent, bg=THEME["bg"], pady=4)
        outer.pack(fill="x")

        top_row = tk.Frame(outer, bg=THEME["bg"])
        top_row.pack(fill="x")
        tk.Label(top_row, text="⏱  TỐC ĐỘ PHÁT LẠI",
            font=("Consolas", 8, "bold"),
            fg=THEME["dim"], bg=THEME["bg"]).pack(side="left")
        self._lbl_speed = tk.Label(top_row, text=f"{self._speed} ms",
            font=("Consolas", 8, "bold"),
            fg=THEME["text"], bg=THEME["bg"])
        self._lbl_speed.pack(side="right")

        self._speed_var = tk.IntVar(value=self._speed)
        sl = tk.Scale(outer,
            from_=50, to=1500, orient="horizontal",
            variable=self._speed_var,
            command=self._on_speed_change,
            bg=THEME["text"], fg=THEME["dim"],
            troughcolor=THEME["header"],
            highlightthickness=0, showvalue=False, sliderrelief="flat")
        sl.pack(fill="x")

        lbl_row = tk.Frame(outer, bg=THEME["bg"])
        lbl_row.pack(fill="x")
        tk.Label(lbl_row, text="Nhanh ←", font=("Consolas", 9),
            fg=THEME["dim"], bg=THEME["bg"]).pack(side="left")
        tk.Label(lbl_row, text="→ Chậm", font=("Consolas", 9),
            fg=THEME["dim"], bg=THEME["bg"]).pack(side="right")

    # ── Buttons (below speed) ──
    def _build_buttons(self, parent):
        def btn(p, text, cmd, bg=None, fg=None):
            return tk.Button(p, text=text, command=cmd,
                font=("Consolas", 9, "bold"),
                bg=bg or THEME["header"],
                fg=fg or THEME["text"],
                activebackground=THEME["accent"],
                activeforeground=THEME["bg"],
                relief="flat", cursor="hand2",
                pady=7, padx=6)

        ctrl = tk.Frame(parent, bg=THEME["bg"])
        ctrl.pack(fill="x", pady=(4, 0))

        # Solve — full width
        self._btn_solve = btn(ctrl, "🔍  Giải thuật toán",
            self._solve, bg="#c0392b", fg="white")
        self._btn_solve.pack(fill="x", pady=(0, 4))

        # Navigation row
        r2 = tk.Frame(ctrl, bg=THEME["bg"])
        r2.pack(fill="x", pady=2)
        for text, cmd in [("⏮ Đầu", self._go_start), ("◀ Trước", self._prev_step),
                          ("Tiếp ▶", self._next_step), ("Cuối ⏭", self._go_end)]:
            btn(r2, text, cmd).pack(side="left", fill="x", expand=True, padx=1)

        # Auto play + Reset
        r3 = tk.Frame(ctrl, bg=THEME["bg"])
        r3.pack(fill="x", pady=2)
        self._btn_auto = btn(r3, "▶▶  Phát tự động",
            self._auto_toggle, bg="#1a5c40", fg="white")
        self._btn_auto.pack(side="left", fill="x", expand=True, padx=(0, 2))
        btn(r3, "↺  Reset", self._reset).pack(side="left", fill="x", expand=True)

    # ── Right panel: info + stats (top) ──
    def _build_info_stats(self, parent):
        # Info
        self._section_label(parent, "THÔNG TIN")
        self._lbl_map = tk.Label(parent,
            font=("Consolas", 11, "bold"),
            fg=THEME["text"], bg=THEME["panel"])
        self._lbl_map.pack(anchor="w")

        row = tk.Frame(parent, bg=THEME["panel"])
        row.pack(fill="x", pady=2)
        self._lbl_step = tk.Label(row, text="Bước: –",
            font=("Consolas", 9), fg=THEME["gold"], bg=THEME["panel"])
        self._lbl_step.pack(side="left")

        self._lbl_status = tk.Label(parent, text="Sẵn sàng",
            font=("Consolas", 10, "bold"), fg=THEME["green"], bg=THEME["panel"])
        self._lbl_status.pack(anchor="w", pady=(0, 4))

        self._divider(parent)

        # Stats cards
        self._section_label(parent, "KẾT QUẢ THUẬT TOÁN")

        r1 = tk.Frame(parent, bg=THEME["panel"])
        r1.pack(fill="x", pady=(0, 6))
        self._card_nodes = self._stat_card(r1, "Nodes duyệt", "–", THEME["blue"])
        self._card_nodes.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self._card_time  = self._stat_card(r1, "Thời gian", "–", THEME["gold"])
        self._card_time.pack(side="left", fill="x", expand=True)

        r2 = tk.Frame(parent, bg=THEME["panel"])
        r2.pack(fill="x")
        self._card_steps = self._stat_card(r2, "Số bước", "–", THEME["green"])
        self._card_steps.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self._card_depth = self._stat_card(r2, "Độ sâu max", "–", THEME["purple"])
        self._card_depth.pack(side="left", fill="x", expand=True)

    # ── Right panel: log (bottom, expands) ──
    def _build_log(self, parent):
        tk.Label(parent, text="📋  NHẬT KÝ BƯỚC ĐI",
            font=("Consolas", 9, "bold"),
            fg=THEME["dim"], bg=THEME["panel"]).pack(anchor="w", pady=(0, 6))

        frame = tk.Frame(parent, bg=THEME["panel"])
        frame.pack(fill="both", expand=True)
        sb = tk.Scrollbar(frame, bg=THEME["panel"])
        sb.pack(side="right", fill="y")
        self._log = tk.Text(frame,
            font=("Consolas", 10), bg=THEME["bg"],
            fg=THEME["text"], relief="flat", wrap="word",
            yscrollcommand=sb.set, state="disabled")
        self._log.pack(fill="both", expand=True)
        sb.config(command=self._log.yview)

    # ── Helpers ──
    def _divider(self, parent):
        tk.Frame(parent, bg=THEME["border"], height=1).pack(fill="x", pady=5)

    def _section_label(self, parent, text):
        tk.Label(parent, text=text,
            font=("Consolas", 8, "bold"),
            fg=THEME["dim"], bg=THEME["panel"]).pack(anchor="w", pady=(0, 4))

    def _stat_card(self, parent, label, value, accent):
        card = tk.Frame(parent, bg=THEME["header"],
                        padx=8, pady=6,
                        highlightbackground=accent,
                        highlightthickness=1)
        tk.Label(card, text=label,
            font=("Consolas", 11), fg=THEME["text"],
            bg=THEME["header"]).pack(anchor="w")
        val_lbl = tk.Label(card, text=value,
            font=("Consolas", 13, "bold"), fg=accent,
            bg=THEME["header"])
        val_lbl.pack(anchor="w")
        card._val_label = val_lbl
        return card

    def _update_stats(self, r=None):
        if r is None:
            for card in (self._card_nodes, self._card_time,
                         self._card_steps, self._card_depth):
                card._val_label.config(text="–")
            return
        self._card_nodes._val_label.config(text=f"{r['nodes_visited']:,}")
        self._card_time._val_label.config(
            text=f"{r['time_elapsed']}s" if r['time_elapsed'] < 10
            else f"{r['time_elapsed']:.1f}s")
        self._card_steps._val_label.config(text=str(r['solution_len']))
        self._card_depth._val_label.config(text=str(r['max_depth']))

    def _log_write(self, msg, color=None):
        self._log.config(state="normal")
        if color:
            tag = f"c_{len(self._log.tag_names())}"
            self._log.tag_config(tag, foreground=color)
            self._log.insert("end", msg + "\n", tag)
        else:
            self._log.insert("end", msg + "\n")
        self._log.see("end")
        self._log.config(state="disabled")

    def _log_clear(self):
        self._log.config(state="normal")
        self._log.delete("1.0", "end")
        self._log.config(state="disabled")

    def _load_map(self):
        m = MAP_OPTIONS[self._map_idx]
        self._canvas.configure(
            width=len(m["grid"][0]) * CELL_SIZE,
            height=len(m["grid"]) * CELL_SIZE)
        self._canvas.cell_size = CELL_SIZE
        self._canvas.draw(m["grid"])
        self._lbl_map.config(text=m["label"])
        self._lbl_step.config(text="Bước: –")
        self._lbl_status.config(text="Sẵn sàng", fg=THEME["green"])
        self._update_stats()
        self._log_clear()
        self._log_write(f"[Map]  {m['label']}", THEME["dim"])
        self._log_write("Nhấn 🔍 Giải để bắt đầu.", THEME["dim"])
        self._result = None
        self._step   = 0
        self._playing = False

    def _refresh_algo_list(self):
        algos = [a[0] for a in ALGO_GROUPS[self._grp_idx]["algos"]]
        self._cb_algo.config(values=algos)
        self._cb_algo.current(0)
        self._algo_idx = 0

    def _build_move_log(self, path):
        """Build step-by-step move log from path."""
        self._log_clear()
        if not path or len(path) < 2:
            self._log_write("Không có bước đi.", THEME["dim"])
            return

        self._log_write(f"Tổng: {len(path)-1} bước", THEME["green"])
        self._log_write("─" * 32, THEME["dim"])

        for i in range(1, len(path)):
            prev_grid, _    = path[i - 1]
            curr_grid, move = path[i]

            if move is None:
                continue

            # Player position before and after
            pr_from, pc_from = find_player(prev_grid)
            pr_to,   pc_to   = find_player(curr_grid)

            arrow = MOVE_ARROW.get(move, move)
            label = MOVE_LABEL.get(move, move)

            # Direction color
            col_map = {
                "UP":    THEME["blue"],
                "DOWN":  THEME["gold"],
                "LEFT":  THEME["purple"],
                "RIGHT": THEME["green"],
            }
            color = col_map.get(move, THEME["text"])

            msg = (f"Bước {i:>3}  {arrow} {label:<7}"
                   f"  ({pr_from},{pc_from})→({pr_to},{pc_to})")
            self._log_write(msg, color)

        self._log.config(state="normal")
        self._log.see("1.0")
        self._log.config(state="disabled")

    # ─────────────────────────────────────── EVENTS ────────────

    def _on_map_change(self):
        self._map_idx = self._map_var.get()
        self._load_map()

    def _on_group_change(self, _=None):
        name = self._grp_var.get()
        self._grp_idx = next(i for i, g in enumerate(ALGO_GROUPS)
                             if g["name"] == name)
        self._refresh_algo_list()

    def _on_algo_change(self, _=None):
        self._algo_idx = self._cb_algo.current()

    def _on_speed_change(self, _=None):
        self._speed = self._speed_var.get()
        self._lbl_speed.config(text=f"{self._speed} ms")

    # ─────────────────────────────────────── SOLVER ────────────

    def _solve(self):
        self._playing = False
        self._btn_auto.config(text="▶▶  Phát tự động", bg="#1a5c40")

        group    = ALGO_GROUPS[self._grp_idx]
        name, fn = group["algos"][self._algo_idx]
        color    = group["color"]

        self._lbl_status.config(text="⏳ Đang tính...", fg=THEME["gold"])
        self._update_stats()
        self._log_clear()
        self._log_write(f"⏳ Đang chạy {group['name']} › {name}…", THEME["gold"])
        self.update()

        grid = copy.deepcopy(MAP_OPTIONS[self._map_idx]["grid"])
        r    = fn(grid)
        self._result = r
        self._step   = 0

        if r["found"]:
            self._lbl_status.config(text="✅  Tìm thấy lời giải!", fg=color)
        else:
            self._lbl_status.config(text="❌  Không tìm thấy", fg=THEME["accent"])

        self._lbl_step.config(text=f"Bước: 0 / {r['solution_len']}")
        self._update_stats(r)

        if r["path"]:
            self._canvas.draw(r["path"][0][0])
            # Build move log
            self._build_move_log(r["path"])
            # Auto-play after short delay
            self.after(600, self._auto_start)
        else:
            self._log_clear()
            self._log_write("❌  Không tìm thấy lời giải.", THEME["accent"])

    def _auto_start(self):
        if self._result and self._result["path"]:
            self._playing = True
            self._btn_auto.config(text="⏸  Dừng lại", bg="#7d1a1a")
            self._tick()

    def _draw_current(self):
        if not self._result or not self._result["path"]:
            return
        grid, move = self._result["path"][self._step]
        vis_list   = self._result.get("visible_list")
        if vis_list and self._step < len(vis_list):
            self._canvas.draw_belief(grid, vis_list[self._step])
        else:
            self._canvas.draw(grid)
        total = self._result["solution_len"]
        self._lbl_step.config(text=f"Bước: {self._step} / {total}")

    def _next_step(self):
        if not self._result: return
        if self._step < len(self._result["path"]) - 1:
            self._step += 1
            self._draw_current()

    def _prev_step(self):
        if not self._result: return
        if self._step > 0:
            self._step -= 1
            self._draw_current()

    def _go_start(self):
        if not self._result: return
        self._step = 0; self._draw_current()

    def _go_end(self):
        if not self._result: return
        self._step = len(self._result["path"]) - 1
        self._draw_current()

    def _auto_toggle(self):
        if not self._result: return
        self._playing = not self._playing
        if self._playing:
            self._btn_auto.config(text="⏸  Dừng lại", bg="#7d1a1a")
            self._tick()
        else:
            self._btn_auto.config(text="▶▶  Phát tự động", bg="#1a5c40")

    def _tick(self):
        if not self._playing: return
        if self._step < len(self._result["path"]) - 1:
            self._step += 1
            self._draw_current()
            self.after(self._speed, self._tick)
        else:
            self._playing = False
            self._btn_auto.config(text="▶▶  Phát tự động", bg="#1a5c40")

    def _reset(self):
        self._playing = False
        self._result  = None
        self._step    = 0
        self._btn_auto.config(text="▶▶  Phát tự động", bg="#1a5c40")
        self._load_map()
