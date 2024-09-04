import tkinter as tk
from tkinter import ttk
from utils.constants import *
from utils.constants import (
    MINI_WINDOW_TITLE, MINI_WINDOW_BG_COLOR, MINI_WINDOW_APM_COLOR,
    MINI_WINDOW_EAPM_COLOR, MINI_WINDOW_LABEL_COLOR, FONT_NAME, MINI_WINDOW_SIZE,
    FONT_WEIGHT_BOLD
)

class MiniWindow:
    def __init__(self, root, tracker):
        self.root = root
        self.tracker = tracker
        self.window = tk.Toplevel(root)
        self.setup_mini_window()

    def setup_mini_window(self):
        self.window.title(MINI_WINDOW_TITLE)
        self.window.attributes('-topmost', True)
        self.window.withdraw()
        self.window.overrideredirect(True)
        self.window.bind('<ButtonRelease-1>', self.snap_to_border)
        self.frame = tk.Frame(self.window, bg=MINI_WINDOW_BG_COLOR)
        self.frame.pack(expand=True, fill='both')

        self.apm_var = tk.StringVar()
        self.eapm_var = tk.StringVar()

        # APM Value and Label
        self.apm_frame = tk.Frame(self.frame, bg=MINI_WINDOW_BG_COLOR)
        self.apm_frame.pack(fill='x', padx=2, pady=(2, 1))
        self.apm_value = tk.Label(self.apm_frame, textvariable=self.apm_var, font=(FONT_NAME, MINI_WINDOW_SIZE, FONT_WEIGHT_BOLD), bg=MINI_WINDOW_BG_COLOR, fg=MINI_WINDOW_APM_COLOR, anchor='e')
        self.apm_value.pack(side='left')
        tk.Label(self.apm_frame, text="APM", font=(FONT_NAME, MINI_WINDOW_SIZE), bg=MINI_WINDOW_BG_COLOR, fg=MINI_WINDOW_LABEL_COLOR).pack(side='right', padx=(1, 0))

        # eAPM Value and Label
        self.eapm_frame = tk.Frame(self.frame, bg=MINI_WINDOW_BG_COLOR)
        self.eapm_frame.pack(fill='x', padx=2, pady=(1, 2))
        self.eapm_value = tk.Label(self.eapm_frame, textvariable=self.eapm_var, font=(FONT_NAME, MINI_WINDOW_SIZE, FONT_WEIGHT_BOLD), bg=MINI_WINDOW_BG_COLOR, fg=MINI_WINDOW_EAPM_COLOR, anchor='e')
        self.eapm_value.pack(side='left')
        tk.Label(self.eapm_frame, text="eAPM", font=(FONT_NAME, MINI_WINDOW_SIZE), bg=MINI_WINDOW_BG_COLOR, fg=MINI_WINDOW_LABEL_COLOR).pack(side='right', padx=(1, 0))

        self.window.bind('<ButtonPress-1>', self.start_move)
        self.window.bind('<B1-Motion>', self.do_move)
        self.window.bind('<Double-Button-1>', self.tracker.gui_manager.toggle_view)

    def snap_to_border(self, event):
        x, y = self.window.winfo_x(), self.window.winfo_y()
        width, height = self.window.winfo_width(), self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        snap_distance = 20  # pixels

        # Snap to left or right border
        if x < snap_distance:
            x = 0
        elif x > screen_width - width - snap_distance:
            x = screen_width - width

        # Snap to top or bottom border
        if y < snap_distance:
            y = 0
        elif y > screen_height - height - snap_distance:
            y = screen_height - height

        self.window.geometry(f"+{x}+{y}")

        # Keep window on top after snapping
        self.window.attributes('-topmost', True)
        self.window.update()

    def update_values(self, current_apm, current_eapm):
        self.apm_var.set(f"{current_apm}")
        self.eapm_var.set(f"{current_eapm}")
        self.adjust_size()

    def adjust_size(self):
        self.window.update_idletasks()
        width = max(self.apm_frame.winfo_reqwidth(), self.eapm_frame.winfo_reqwidth())
        height = self.apm_frame.winfo_reqheight() + self.eapm_frame.winfo_reqheight()

        # Add minimal padding
        width += 4
        height += 4

        self.window.geometry(f"{width}x{height}")

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")

    def show(self):
        self.window.deiconify()
        self.adjust_size()  # Ensure correct size when shown

    def hide(self):
        self.window.withdraw()
