import tkinter as tk
from tkinter import ttk
from utils.constants import *
# from utils.font_loader import get_font

class MiniWindow:
    def __init__(self, root, tracker):
        self.root = root
        self.tracker = tracker
        # self.custom_fonts = custom_fonts
        self.window = tk.Toplevel(root)
        self.setup_mini_window()

    def setup_mini_window(self):
        self.window.title("APM Tracker Mini")
        self.window.attributes('-topmost', True)
        self.window.withdraw()
        self.window.overrideredirect(True)

        self.frame = tk.Frame(self.window, bg='#2E3440')  # Nord theme background color
        self.frame.pack(expand=True, fill='both')

        self.apm_var = tk.StringVar()
        self.eapm_var = tk.StringVar()

        # value_font = get_font(self.custom_fonts, 12, "bold")
        # label_font = get_font(self.custom_fonts, 10)

        # APM Value and Label
        self.apm_frame = tk.Frame(self.frame, bg='#2E3440')
        self.apm_frame.pack(fill='x', padx=2, pady=(2, 1))
        self.apm_value = tk.Label(self.apm_frame, textvariable=self.apm_var, font=(FONT_NAME, MINI_WINDOW_SIZE, "bold"), bg=MINI_WINDOW_BG_COLOR, fg=MINI_WINDOW_APM_COLOR, anchor='e')
        self.apm_value.pack(side='left')
        tk.Label(self.apm_frame, text="APM", font=(FONT_NAME, MINI_WINDOW_SIZE ), bg=MINI_WINDOW_BG_COLOR, fg=MINI_WINDOW_LABEL_COLOR).pack(side='right', padx=(1, 0))

        # eAPM Value and Label
        self.eapm_frame = tk.Frame(self.frame, bg='#2E3440')
        self.eapm_frame.pack(fill='x', padx=2, pady=(1, 2))
        self.eapm_value = tk.Label(self.eapm_frame, textvariable=self.eapm_var, font=(FONT_NAME, MINI_WINDOW_SIZE, "bold"), bg=MINI_WINDOW_BG_COLOR, fg=MINI_WINDOW_EAPM_COLOR, anchor='e')
        self.eapm_value.pack(side='left')
        tk.Label(self.eapm_frame, text="eAPM", font=(FONT_NAME, MINI_WINDOW_SIZE), bg=MINI_WINDOW_BG_COLOR, fg=MINI_WINDOW_LABEL_COLOR).pack(side='right', padx=(1, 0))

        self.window.bind('<ButtonPress-1>', self.start_move)
        self.window.bind('<B1-Motion>', self.do_move)
        self.window.bind('<Double-Button-1>', self.tracker.gui_manager.toggle_view)

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
