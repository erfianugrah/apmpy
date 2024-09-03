import tkinter as tk
from tkinter import ttk
from utils.font_loader import get_font

class MiniWindow:
    def __init__(self, root, tracker, custom_fonts):
        self.root = root
        self.tracker = tracker
        self.custom_fonts = custom_fonts
        self.window = tk.Toplevel(root)
        self.setup_mini_window()

    def setup_mini_window(self):
        self.window.title("APM Tracker Mini")
        self.window.geometry("150x70")
        self.window.attributes('-topmost', True)
        self.window.withdraw()

        self.window.overrideredirect(True)

        self.frame = tk.Frame(self.window, bg=self.tracker.gui_manager.bg_color)
        self.frame.pack(expand=True, fill='both')

        self.apm_var = tk.StringVar()
        self.eapm_var = tk.StringVar()

        label_font = get_font(self.custom_fonts, 12)

        self.apm_label = tk.Label(self.frame, textvariable=self.apm_var, font=label_font, bg=self.tracker.gui_manager.bg_color)
        self.apm_label.pack(anchor='w', padx=5, pady=2)
        self.eapm_label = tk.Label(self.frame, textvariable=self.eapm_var, font=label_font, bg=self.tracker.gui_manager.bg_color)
        self.eapm_label.pack(anchor='w', padx=5, pady=2)

        self.window.bind('<ButtonPress-1>', self.start_move)
        self.window.bind('<B1-Motion>', self.do_move)
        self.window.bind('<Double-Button-1>', self.tracker.gui_manager.toggle_view)

    def update_values(self, current_apm, current_eapm):
        self.apm_var.set(f"APM: {current_apm}")
        self.eapm_var.set(f"eAPM: {current_eapm}")

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

    def hide(self):
        self.window.withdraw()

    def adjust_size(self):
        self.apm_label.update_idletasks()
        self.eapm_label.update_idletasks()

        width = max(self.apm_label.winfo_reqwidth(), self.eapm_label.winfo_reqwidth())
        height = self.apm_label.winfo_reqheight() + self.eapm_label.winfo_reqheight()

        width += 10
        height += 10

        self.window.geometry(f"{width}x{height}")
