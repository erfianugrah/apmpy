import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import os
from utils.font_loader import load_custom_font

class MainFrame:
    def __init__(self, parent, tracker, custom_fonts):
        self.parent = parent
        self.tracker = tracker
        self.custom_fonts = custom_fonts
        self.frame = ttk.Frame(parent, style='MainFrame.TFrame')
        self.setup_styles()
        self.setup_main_frame()

    def setup_styles(self):
        style = ttk.Style()
        style.configure('MainFrame.TFrame', background='#282c34')
        style.configure('Title.TLabel', background='#282c34', foreground='#61afef', font=get_font(self.custom_fonts, 24))
        style.configure('Subtitle.TLabel', background='#282c34', foreground='#98c379', font=get_font(self.custom_fonts, 14))
        style.configure('Data.TLabel', background='#3e4451', foreground='#e5c07b', font=get_font(self.custom_fonts, 20))
        style.configure('DataLabel.TLabel', background='#3e4451', foreground='#abb2bf', font=get_font(self.custom_fonts, 12))
        style.configure('DataFrame.TFrame', background='#3e4451')
        style.configure('Toggle.TButton', font=get_font(self.custom_fonts, 12))

    def setup_styles(self):
        style = ttk.Style()
        style.configure('MainFrame.TFrame', background='#282c34')
        style.configure('Title.TLabel', background='#282c34', foreground='#61afef', font=('IosevkaTerm NF', 24, 'bold'))
        style.configure('Subtitle.TLabel', background='#282c34', foreground='#98c379', font=('IosevkaTerm NF', 14))
        style.configure('Data.TLabel', background='#3e4451', foreground='#e5c07b', font=('IosevkaTerm NF', 20, 'bold'))
        style.configure('DataLabel.TLabel', background='#3e4451', foreground='#abb2bf', font=('IosevkaTerm NF', 12))
        style.configure('DataFrame.TFrame', background='#3e4451')
        style.configure('Toggle.TButton', font=('IosevkaTerm NF', 12, 'bold'))

    def setup_main_frame(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        # Title
        ttk.Label(self.frame, text="APM Tracker", style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(20, 5))
        ttk.Label(self.frame, text="Monitor your Actions Per Minute", style='Subtitle.TLabel').grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # Current APM and eAPM
        self.create_data_display(2, 0, "Current APM", 'current_apm_var', '#61afef')
        self.create_data_display(2, 1, "Current eAPM", 'current_eapm_var', '#98c379')

        # Peak APM and eAPM
        self.create_data_display(3, 0, "Peak APM", 'peak_apm_var', '#e06c75')
        self.create_data_display(3, 1, "Peak eAPM", 'peak_eapm_var', '#d19a66')

        # Average APM and eAPM
        self.create_data_display(4, 0, "Average APM", 'avg_apm_var', '#c678dd')
        self.create_data_display(4, 1, "Average eAPM", 'avg_eapm_var', '#56b6c2')

        # Toggle Mini View Button
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
