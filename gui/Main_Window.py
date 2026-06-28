# gui/main_window.py

import tkinter as tk
from tkinter import ttk
import copy

from core.Renderer import MapCanvas, THEME, CELL
from core.Game import find_player, DIRECTIONS

from algorithms.Uninformed_Search   import solve_bfs #, solve_dfs, solve_ucs
from algorithms.Informed_Search     import solve_idastar #, solve_astar, solve_greedy
from algorithms.Local_Search        import solve_hill_climbing #, solve_simulated_annealing, solve_local_beam
from algorithms.Constraint_Satisfaction_Problems     import solve_backtracking #, solve_bomb_forward_checking, solve_bomb_min_conflicts
#from algorithms.Adversarial_Search      import  solve_alphabeta#, solve_minimax, solve_expectimax
from algorithms.Complex_Environments    import solve_partial_observation#, solve_and_or, solve_no_observation

MAP_OPTIONS = [
    {
        "label": "Map 1 – 2 thùng, ít vật cản",
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
    {
        "label": "Map 2 – 2 thùng, nhiều vật cản",
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
    {
        "label": "Map 3 – 3 thùng, 3 đích",
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
]

ALGO_GROUPS = [
    {"name": "Uninformed Search", "color": "#4ecca3",
        "algos": [("BFS", solve_bfs),]}, #("DFS", solve_dfs), ("UCS", solve_ucs)]},
    {"name": "Informed Search",   "color": "#74b9ff",
     "algos": [("IDA*", solve_idastar),]}, #("Greedy", solve_greedy), ("A*", solve_astar)]},
    {"name": "Local Search",      "color": "#f5a623",
     "algos": [("Hill Climbing", solve_hill_climbing),]},
               #("Simulated Annealing", solve_simulated_annealing),
               #("Local Beam Search", solve_local_beam)]},
    {"name": "CSP",               "color": "#a29bfe",
     "algos": [("Backtracking", solve_backtracking),]},
               #("Forward Checking", solve_forward_checking),
               #("Min-Conflicts", solve_min_conflicts)]},
   # {"name": "Adversarial Search","color": "#e94560",
    # "algos": [("Alpha-Beta", solve_alphabeta),]},
                #("Minimax", solve_minimax),
               #("Expectimax", solve_expectimax)]},
    {"name": "Belief State",      "color": "#fd79a8",
     "algos": [("Partial Observation", solve_partial_observation),]},
              # ("AND-OR Graph", solve_and_or), ("Sensorless", solve_no_observation)]},
]

# Canvas cell size
CELL_SIZE = 60

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
        self._history  = []   # list of dicts: algo, map, time, found

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

        self._build_map_selector(left)

        # Chú thích bên trái, map bên phải – căn trái
        map_row = tk.Frame(left, bg=THEME["bg"])
        map_row.pack(anchor="w", pady=4)

        legend_frame = tk.Frame(map_row, bg=THEME["bg"])
        legend_frame.pack(side="left", anchor="n", padx=(0, 14))

        canvas_frame = tk.Frame(map_row, bg=THEME["bg"])
        canvas_frame.pack(side="left", anchor="n")

        self._build_legend(legend_frame)
        self._build_canvas_area(canvas_frame)

        self._build_buttons(left)

        # ── Right: top = info+stats, bottom = log/history tabs ──
        right = tk.Frame(body, bg=THEME["bg"])
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=0)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        top_panel = tk.Frame(right, bg=THEME["panel"], padx=14, pady=10)
        top_panel.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self._build_info_stats(top_panel)
        self._build_speed_control(top_panel)

        log_frame = tk.Frame(right, bg=THEME["panel"], padx=14, pady=10)
        log_frame.grid(row=1, column=0, sticky="nsew")
        self._build_log_tabs(log_frame)

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
            text="Uninformed · Informed · Local · CSP💣 · Adversarial · Belief",
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
        self._canvas_frame.pack()
        dummy = MAP_OPTIONS[0]["grid"]
        self._canvas = MapCanvas(self._canvas_frame, dummy, cell_size=CELL_SIZE)
        self._canvas.pack()

    def _build_legend(self, parent):
        # Section title sát trái
        tk.Label(parent, text="CHÚ THÍCH",
            font=("Consolas", 8, "bold"),
            fg=THEME["dim"], bg=THEME["bg"]).pack(anchor="w", pady=(0, 4))

        items = [
            ("■", THEME["gold"],   "Thùng"),
            ("◎", THEME["green"],  "Đích"),
            ("✓", THEME["accent"], "Thùng @ Đích"),
            ("●", THEME["green"],  "Người"),
            ("█", "#2d333b",       "Tường"),
            ("💣", "#a29bfe",      "Bom (CSP)"),
            ("💥", "#ff6600",      "Nổ phá tường"),
        ]
        for sym, col, lbl in items:
            row = tk.Frame(parent, bg=THEME["bg"])
            row.pack(anchor="w", pady=1)
            tk.Label(row, text=sym, fg=col, bg=THEME["bg"],
                font=("Arial", 13, "bold"), width=2, anchor="w").pack(side="left")
            tk.Label(row, text=lbl, fg=THEME["dim"], bg=THEME["bg"],
                font=("Consolas", 10), anchor="w").pack(side="left")

    # ── Speed control ──
    def _build_speed_control(self, parent):
        outer = tk.Frame(parent, bg=THEME["panel"], pady=4)
        outer.pack(fill="x")

        top_row = tk.Frame(outer, bg=THEME["panel"])
        top_row.pack(fill="x")
        tk.Label(top_row, text="⏱  TỐC ĐỘ PHÁT LẠI",
            font=("Consolas", 8, "bold"),
            fg=THEME["dim"], bg=THEME["panel"]).pack(side="left")
        self._lbl_speed = tk.Label(top_row, text=f"{self._speed} ms",
            font=("Consolas", 8, "bold"),
            fg=THEME["text"], bg=THEME["panel"])
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

        lbl_row = tk.Frame(outer, bg=THEME["panel"])
        lbl_row.pack(fill="x")
        tk.Label(lbl_row, text="Nhanh ←", font=("Consolas", 9),
            fg=THEME["dim"], bg=THEME["panel"]).pack(side="left")
        tk.Label(lbl_row, text="→ Chậm", font=("Consolas", 9),
            fg=THEME["dim"], bg=THEME["panel"]).pack(side="right")

    # ── Buttons ──
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

        self._btn_solve = btn(ctrl, "🔍  Giải thuật toán",
            self._solve, bg="#c0392b", fg="white")
        self._btn_solve.pack(fill="x", pady=(0, 4))

        r2 = tk.Frame(ctrl, bg=THEME["bg"])
        r2.pack(fill="x", pady=2)
        for text, cmd in [("⏮ Đầu", self._go_start), ("◀ Trước", self._prev_step),
                          ("Tiếp ▶", self._next_step), ("Cuối ⏭", self._go_end)]:
            btn(r2, text, cmd).pack(side="left", fill="x", expand=True, padx=1)

        r3 = tk.Frame(ctrl, bg=THEME["bg"])
        r3.pack(fill="x", pady=2)
        self._btn_auto = btn(r3, "▶▶  Phát tự động",
            self._auto_toggle, bg="#1a5c40", fg="white")
        self._btn_auto.pack(side="left", fill="x", expand=True, padx=(0, 2))
        btn(r3, "↺  Reset", self._reset).pack(side="left", fill="x", expand=True)

    # ── Right panel: info + stats (top) ──
    def _build_info_stats(self, parent):
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

    # ── Right panel: log + history tabs ──
    def _build_log_tabs(self, parent):
        # Tab bar
        tab_bar = tk.Frame(parent, bg=THEME["panel"])
        tab_bar.pack(fill="x", pady=(0, 6))

        self._active_tab = tk.StringVar(value="log")

        self._btn_tab_log = tk.Button(tab_bar,
            text="📋  Nhật ký bước đi",
            font=("Consolas", 9, "bold"),
            relief="flat", cursor="hand2",
            pady=5, padx=10,
            command=lambda: self._switch_tab("log"))
        self._btn_tab_log.pack(side="left")

        self._btn_tab_hist = tk.Button(tab_bar,
            text="🕓  Lịch sử",
            font=("Consolas", 9, "bold"),
            relief="flat", cursor="hand2",
            pady=5, padx=10,
            command=lambda: self._switch_tab("history"))
        self._btn_tab_hist.pack(side="left", padx=(4, 0))

        # Container cố định — 2 frame chồng lên nhau trong cùng ô grid
        stack = tk.Frame(parent, bg=THEME["panel"])
        stack.pack(fill="both", expand=True)
        stack.rowconfigure(0, weight=1)
        stack.columnconfigure(0, weight=1)

        # ── Log frame ──
        self._tab_log_frame = tk.Frame(stack, bg=THEME["panel"])
        self._tab_log_frame.grid(row=0, column=0, sticky="nsew")

        log_inner = tk.Frame(self._tab_log_frame, bg=THEME["panel"])
        log_inner.pack(fill="both", expand=True)
        sb = tk.Scrollbar(log_inner, bg=THEME["panel"])
        sb.pack(side="right", fill="y")
        self._log = tk.Text(log_inner,
            font=("Consolas", 10), bg=THEME["bg"],
            fg=THEME["text"], relief="flat", wrap="word",
            yscrollcommand=sb.set, state="disabled")
        self._log.pack(fill="both", expand=True)
        sb.config(command=self._log.yview)

        # ── History frame ──
        self._tab_hist_frame = tk.Frame(stack, bg=THEME["panel"])
        self._tab_hist_frame.grid(row=0, column=0, sticky="nsew")

        cols = ("algo", "map", "time", "steps", "found")
        style = ttk.Style()
        style.configure("History.Treeview",
            background=THEME["bg"],
            foreground=THEME["text"],
            fieldbackground=THEME["bg"],
            rowheight=24,
            font=("Consolas", 9))
        style.configure("History.Treeview.Heading",
            background=THEME["header"],
            foreground=THEME["text"],
            font=("Consolas", 9, "bold"),
            relief="flat")
        style.map("History.Treeview",
            background=[("selected", THEME["header"])],
            foreground=[("selected", THEME["accent"])])

        hist_inner = tk.Frame(self._tab_hist_frame, bg=THEME["panel"])
        hist_inner.pack(fill="both", expand=True)

        sb_h = tk.Scrollbar(hist_inner, bg=THEME["panel"])
        sb_h.pack(side="right", fill="y")

        self._hist_tree = ttk.Treeview(hist_inner, columns=cols,
            show="headings", style="History.Treeview",
            yscrollcommand=sb_h.set)
        sb_h.config(command=self._hist_tree.yview)

        self._hist_tree.heading("algo",  text="Thuật toán")
        self._hist_tree.heading("map",   text="Map")
        self._hist_tree.heading("time",  text="Thời gian")
        self._hist_tree.heading("steps", text="Số bước")
        self._hist_tree.heading("found", text="Lời giải")
        

        self._hist_tree.column("algo",  width=130, anchor="w")
        self._hist_tree.column("map",   width=80,  anchor="center")
        self._hist_tree.column("time",  width=80,  anchor="center")
        self._hist_tree.column("steps", width=80,  anchor="center")
        self._hist_tree.column("found", width=80,  anchor="center")

        self._hist_tree.pack(fill="both", expand=True)

        btn_clear = tk.Button(self._tab_hist_frame, text="🗑  Xóa lịch sử",
            font=("Consolas", 8, "bold"),
            bg=THEME["header"], fg=THEME["dim"],
            activebackground=THEME["accent"], activeforeground=THEME["bg"],
            relief="flat", cursor="hand2", pady=4,
            command=self._clear_history)
        btn_clear.pack(pady=(6, 0))

        # Init tab — lift log lên trên
        self._switch_tab("log")

    def _switch_tab(self, tab):
        self._active_tab.set(tab)
        active_bg   = THEME["accent"]
        inactive_bg = THEME["header"]
        active_fg   = THEME["bg"]
        inactive_fg = THEME["text"]

        if tab == "log":
            self._btn_tab_log.config(bg=active_bg, fg=active_fg)
            self._btn_tab_hist.config(bg=inactive_bg, fg=inactive_fg)
            self._tab_log_frame.lift()   # đưa log lên trên, hist vẫn ở đó
        else:
            self._btn_tab_hist.config(bg=active_bg, fg=active_fg)
            self._btn_tab_log.config(bg=inactive_bg, fg=inactive_fg)
            self._tab_hist_frame.lift()  # đưa history lên trên, log vẫn ở đó

    def _add_history(self, algo_name, map_label, time_elapsed, steps, found):
        found_str = "✅ Có" if found else "❌ Không"
        time_str  = f"{time_elapsed}s" if time_elapsed < 10 else f"{time_elapsed:.1f}s"
        steps_str = str(steps) if found else "–"
        self._hist_tree.insert("", 0, values=(algo_name, map_label, time_str, steps_str, found_str))
    def _clear_history(self):
        for item in self._hist_tree.get_children():
            self._hist_tree.delete(item)

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
        # Nếu đang ở nhóm CSP thì ghi chú chế độ bom
        grp_name = ALGO_GROUPS[self._grp_idx]["name"] if hasattr(self, "_grp_idx") else ""
        if grp_name == "CSP":
            self._log_write("💣  Chế độ Bom Nổ: CSP tìm vị trí đặt Bom,", "#a29bfe")
            self._log_write("    BFS đẩy Bom đến vị trí, Bom nổ phá tường!", "#a29bfe")
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
            pr_from, pc_from = find_player(prev_grid)
            pr_to,   pc_to   = find_player(curr_grid)
            arrow = MOVE_ARROW.get(move, move)
            label = MOVE_LABEL.get(move, move)
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

    def _build_bomb_log(self, r):
        """Nhật ký riêng cho chế độ Bom Nổ."""
        self._log_clear()
        bomb_positions = r.get("bomb_positions", [])
        exp_step = r.get("explosion_step", 0)
        total = r["solution_len"]

        self._log_write("💣  CHẾ ĐỘ Bom NỔ (CSP + BFS)", "#a29bfe")
        self._log_write("─" * 36, THEME["dim"])
        self._log_write(f"CSP tìm được {len(bomb_positions)} vị trí kích bom:", THEME["gold"])
        for i, (br, bc) in enumerate(bomb_positions):
            self._log_write(f"  Bom {i+1}: ô ({br}, {bc})", "#e17055")
        self._log_write("─" * 36, THEME["dim"])
        self._log_write(f"BFS đẩy Bom: {exp_step} bước", THEME["green"])
        self._log_write(f"Di chuyển an toàn: {total - exp_step - 1} bước", THEME["blue"])
        self._log_write(f"Tổng: {total} bước + 1 vụ nổ", THEME["text"])
        self._log_write("─" * 36, THEME["dim"])
        self._log_write("⚠️  Bán kính nổ: 8 ô xung quanh mỗi Bom", THEME["gold"])
        self._log_write("✅  Nhân vật đã di chuyển ra khỏi vùng nổ", THEME["green"])

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
        map_label = MAP_OPTIONS[self._map_idx]["label"]

        self._lbl_status.config(text="⏳ Đang tính...", fg=THEME["gold"])
        self._update_stats()
        self._log_clear()
        self._log_write(f"⏳ Đang chạy {group['name']} › {name}…", THEME["gold"])
        # Switch to log tab when solving
        self._switch_tab("log")
        self.update()

        grid = copy.deepcopy(MAP_OPTIONS[self._map_idx]["grid"])
        r    = fn(grid)
        self._result = r
        self._step   = 0

        if r["found"]:
            if r.get("mode") == "bomb":
                self._lbl_status.config(text="💣  Bom đã được đặt! Sẵn sàng nổ!", fg=color)
            else:
                self._lbl_status.config(text="✅  Tìm thấy lời giải!", fg=color)
        else:
            self._lbl_status.config(text="❌  Không tìm thấy", fg=THEME["accent"])

        self._lbl_step.config(text=f"Bước: 0 / {r['solution_len']}")
        self._update_stats(r)

        # Add to history
        self._add_history(f"{group['name']} › {name}", map_label,
                  r["time_elapsed"], r["solution_len"], r["found"])

        if r["path"]:
            self._canvas.draw(r["path"][0][0])
            if r.get("mode") == "bomb":
                self._build_bomb_log(r)
            else:
                self._build_move_log(r["path"])
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
        exp_step   = self._result.get("explosion_step", -1)
        if vis_list and self._step < len(vis_list):
            self._canvas.draw_belief(grid, vis_list[self._step])
        else:
            self._canvas.draw(grid)
        total = self._result["solution_len"]
        # Hiển thị nhãn đặc biệt ở bước nổ
        if self._result.get("mode") == "bomb":
            if self._step == len(self._result["path"]) - 1:
                self._lbl_step.config(text=f"💥 Bom NỔ! Tường bị phá!")
                self._lbl_status.config(text="💥  Nổ! Tường đã bị phá!", fg="#ff6600")
            elif self._step > exp_step and exp_step >= 0:
                self._lbl_step.config(text=f"🏃 Chạy về vị trí an toàn… {self._step}/{total}")
            else:
                self._lbl_step.config(text=f"💣 Đẩy Bom… Bước {self._step} / {total}")
        else:
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
