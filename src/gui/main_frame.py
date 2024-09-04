import tkinter as tk
from tkinter import ttk
from utils.constants import (
    BACKGROUND_COLOR, FRAME_BACKGROUND_COLOR, TITLE_COLOR, SUBTITLE_COLOR,
    DATA_COLOR, DATA_LABEL_COLOR, TITLE_FONT_SIZE, SUBTITLE_FONT_SIZE,
    DATA_FONT_SIZE, LABEL_FONT_SIZE, FONT_NAME
)

class MainFrame:
    def __init__(self, parent, tracker):
        self.parent = parent
        self.tracker = tracker
        self.frame = ttk.Frame(parent, style='MainFrame.TFrame')
        self.setup_styles()
        self.setup_main_frame()

    def setup_styles(self):
        style = ttk.Style()
        style.configure('MainFrame.TFrame', background=BACKGROUND_COLOR)
        style.configure('Title.TLabel', background=BACKGROUND_COLOR, foreground=TITLE_COLOR, font=(FONT_NAME, TITLE_FONT_SIZE))
        style.configure('Subtitle.TLabel', background=BACKGROUND_COLOR, foreground=SUBTITLE_COLOR, font=(FONT_NAME, SUBTITLE_FONT_SIZE))
        style.configure('Data.TLabel', background=FRAME_BACKGROUND_COLOR, foreground=DATA_COLOR, font=(FONT_NAME, DATA_FONT_SIZE))
        style.configure('DataLabel.TLabel', background=FRAME_BACKGROUND_COLOR, foreground=DATA_LABEL_COLOR, font=(FONT_NAME, LABEL_FONT_SIZE))
        style.configure('DataFrame.TFrame', background=FRAME_BACKGROUND_COLOR)
        style.configure('Toggle.TButton', font=(FONT_NAME, LABEL_FONT_SIZE))

    def setup_main_frame(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        ttk.Label(self.frame, text="APM Tracker", style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(20, 5))
        ttk.Label(self.frame, text="Monitor your Actions Per Minute", style='Subtitle.TLabel').grid(row=1, column=0, columnspan=2, pady=(0, 20))

        self.create_data_display(2, 0, "Current APM", 'current_apm_var', TITLE_COLOR)
        self.create_data_display(2, 1, "Current eAPM", 'current_eapm_var', SUBTITLE_COLOR)
        self.create_data_display(3, 0, "Peak APM", 'peak_apm_var', '#e06c75')
        self.create_data_display(3, 1, "Peak eAPM", 'peak_eapm_var', '#d19a66')
        self.create_data_display(4, 0, "Average APM", 'avg_apm_var', '#c678dd')
        self.create_data_display(4, 1, "Average eAPM", 'avg_eapm_var', '#56b6c2')

        ttk.Button(self.frame, text="Toggle Mini View", style='Toggle.TButton', command=self.tracker.gui_manager.toggle_view).grid(row=5, column=0, columnspan=2, pady=20)

    def create_data_display(self, row, column, label_text, var_name, color):
        frame = ttk.Frame(self.frame, style='DataFrame.TFrame')
        frame.grid(row=row, column=column, padx=10, pady=10, sticky='nsew')
        
        ttk.Label(frame, text=label_text, style='DataLabel.TLabel').pack(pady=(5, 0))
        setattr(self, var_name, tk.StringVar())
        data_label = ttk.Label(frame, textvariable=getattr(self, var_name), style='Data.TLabel')
        data_label.pack(pady=(0, 5))
        data_label.configure(foreground=color)

    def update_values(self, current_apm, current_eapm, peak_apm, peak_eapm, avg_apm, avg_eapm):
        self.current_apm_var.set(f"{current_apm}")
        self.current_eapm_var.set(f"{current_eapm}")
        self.peak_apm_var.set(f"{peak_apm}")
        self.peak_eapm_var.set(f"{peak_eapm}")
        self.avg_apm_var.set(f"{avg_apm:.2f}")
        self.avg_eapm_var.set(f"{avg_eapm:.2f}")
