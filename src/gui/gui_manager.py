import tkinter as tk
from tkinter import ttk
import logging
from utils import get_icon_path, set_window_icon, set_appwindow
import platform

from .main_frame import MainFrame
from .graph_frame import GraphFrame
from .settings_frame import SettingsFrame
from .mini_window import MiniWindow

class GUIManager:
    def __init__(self, tracker):
        self.tracker = tracker
        self.root = None
        self.mini_window = None
        self.graph_needs_update = True
        self.is_mini_view = False
        self.bg_color = '#F5F5F5'
        self.icon_path = get_icon_path()

    def setup_gui(self):
        self.root = tk.Tk()
        set_window_icon(self.root, self.icon_path)
        self.root.title("APM Tracker")
        self.root.geometry("600x400")
        self.root.protocol("WM_DELETE_WINDOW", self.tracker.on_closing)
        self.setup_notebook()
        self.setup_custom_font()
        self.create_mini_window()
        self.root.bind('<Control-m>', self.toggle_view) 

    def setup_notebook(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        self.main_frame = MainFrame(self.notebook, self.tracker)
        self.graph_frame = GraphFrame(self.notebook, self.tracker)
        self.settings_frame = SettingsFrame(self.notebook, self.tracker)

        self.notebook.add(self.main_frame.frame, text='Main')
        self.notebook.add(self.graph_frame.frame, text='Graph')
        self.notebook.add(self.settings_frame.frame, text='Settings')

    def setup_custom_font(self):
        self.custom_font = tk.font.Font(family="Segoe UI", size=12)

    def create_mini_window(self):
        self.mini_window = MiniWindow(self.root, self.tracker)

    def update_transparency(self, value):
        alpha = float(value)
        if self.root:
            self.root.attributes('-alpha', alpha)
        if self.mini_window:
            self.mini_window.window.attributes('-alpha', alpha)

    def toggle_view(self, event=None):
        self.is_mini_view = not self.is_mini_view
        if self.is_mini_view:
            self.root.withdraw()
            self.mini_window.show()
            if platform.system() == 'Windows':
                set_appwindow(self.mini_window.window)
        else:
            self.mini_window.hide()
            self.root.deiconify()

    def update_gui(self):
        if not self.tracker.running:
            return

        current_apm = self.tracker.data_manager.calculate_current_apm()
        current_eapm = self.tracker.data_manager.calculate_current_eapm()
        avg_apm = self.tracker.data_manager.calculate_average_apm()
        avg_eapm = self.tracker.data_manager.calculate_average_eapm()

        self.tracker.data_manager.peak_apm = max(self.tracker.data_manager.peak_apm, current_apm)
        self.tracker.data_manager.peak_eapm = max(self.tracker.data_manager.peak_eapm, current_eapm)

        self.main_frame.update_values(current_apm, current_eapm, 
                                      self.tracker.data_manager.peak_apm, 
                                      self.tracker.data_manager.peak_eapm,
                                      avg_apm, avg_eapm)

        self.mini_window.update_values(current_apm, current_eapm)
        self.mini_window.adjust_size()

        self.update_job = self.root.after(self.tracker.settings_manager.update_interval, self.update_gui)

    def update_graph_settings(self):
        self.graph_frame.update_graph_settings()

    def run_main_loop(self):
        if self.root:
            self.update_gui()
            self.root.mainloop()
        else:
            logging.error("Error: Main window (root) is not initialized.")
