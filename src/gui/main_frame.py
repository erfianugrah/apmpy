import tkinter as tk
from tkinter import ttk

class MainFrame:
    def __init__(self, parent, tracker):
        self.parent = parent
        self.tracker = tracker
        self.frame = ttk.Frame(parent)
        self.setup_main_frame()

    def setup_main_frame(self):
        font_large = ("Helvetica", 24, 'bold')

        self.current_apm_var = tk.StringVar()
        self.current_eapm_var = tk.StringVar()
        self.peak_apm_var = tk.StringVar()
        self.peak_eapm_var = tk.StringVar()
        self.avg_apm_var = tk.StringVar()
        self.avg_eapm_var = tk.StringVar()
        
        ttk.Label(self.frame, textvariable=self.current_apm_var, font=font_large, foreground='blue').pack(pady=10)
        ttk.Label(self.frame, textvariable=self.current_eapm_var, font=font_large, foreground='green').pack(pady=10)
        ttk.Label(self.frame, textvariable=self.peak_apm_var).pack(pady=5)
        ttk.Label(self.frame, textvariable=self.peak_eapm_var).pack(pady=5)
        ttk.Label(self.frame, textvariable=self.avg_apm_var).pack(pady=5)
        ttk.Label(self.frame, textvariable=self.avg_eapm_var).pack(pady=5)

        ttk.Button(self.frame, text="Toggle Mini View", command=self.tracker.gui_manager.toggle_view).pack(pady=10)

    def update_values(self, current_apm, current_eapm, peak_apm, peak_eapm, avg_apm, avg_eapm):
        self.current_apm_var.set(f"Current APM: {current_apm}")
        self.current_eapm_var.set(f"Current eAPM: {current_eapm}")
        self.peak_apm_var.set(f"Peak APM: {peak_apm}")
        self.peak_eapm_var.set(f"Peak eAPM: {peak_eapm}")
        self.avg_apm_var.set(f"Average APM: {avg_apm:.2f}")
        self.avg_eapm_var.set(f"Average eAPM: {avg_eapm:.2f}")
