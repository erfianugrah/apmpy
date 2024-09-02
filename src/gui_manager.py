import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import logging
from utils import get_icon_path, set_window_icon, set_appwindow
import platform
import numpy as np

class GUIManager:
    def __init__(self, tracker):
        self.tracker = tracker
        self.root = None
        self.mini_window = None
        self.graph_needs_update = True
        self.is_mini_view = False
        self.last_mini_size = (0, 0)
        self.bg_color = '#F5F5F5'
        self.icon_path = get_icon_path()
        self.update_interval = 500
        self.max_actions_per_second = 10  # Maximum actions per second to display

    def setup_gui(self):
        self.root = tk.Tk()
        set_window_icon(self.root, self.icon_path)
        self.root.title("APM Tracker")
        self.root.geometry("600x400")
        self.root.protocol("WM_DELETE_WINDOW", self.tracker.on_closing)

        self.setup_notebook()
        self.setup_custom_font()
        self.create_mini_window()

    def setup_notebook(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        self.main_frame = ttk.Frame(self.notebook)
        self.graph_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.main_frame, text='Main')
        self.notebook.add(self.graph_frame, text='Graph')
        self.notebook.add(self.settings_frame, text='Settings')

        self.setup_main_frame()
        self.setup_graph_frame()
        self.setup_settings_frame()

    def setup_custom_font(self):
        self.custom_font = tkfont.Font(family="Segoe UI", size=12)

    def create_mini_window(self):
        self.mini_window = tk.Toplevel(self.root)
        self.mini_window.title("APM Tracker Mini")
        self.mini_window.geometry("150x70")
        self.mini_window.attributes('-topmost', True)
        self.mini_window.withdraw()

        set_window_icon(self.mini_window, self.icon_path)

        self.mini_window.overrideredirect(True)

        self.mini_frame = tk.Frame(self.mini_window, bg=self.bg_color)
        self.mini_frame.pack(expand=True, fill='both')

        self.mini_apm_var = tk.StringVar()
        self.mini_eapm_var = tk.StringVar()

        self.mini_apm_label = tk.Label(self.mini_frame, textvariable=self.mini_apm_var, font=self.custom_font, bg=self.bg_color)
        self.mini_apm_label.pack(anchor='w', padx=5, pady=2)
        self.mini_eapm_label = tk.Label(self.mini_frame, textvariable=self.mini_eapm_var, font=self.custom_font, bg=self.bg_color)
        self.mini_eapm_label.pack(anchor='w', padx=5, pady=2)

        self.mini_window.bind('<ButtonPress-1>', self.start_move)
        self.mini_window.bind('<B1-Motion>', self.do_move)
        self.mini_window.bind('<Double-Button-1>', self.toggle_view)

    def setup_main_frame(self):
        font_large = ("Helvetica", 24, 'bold')

        self.current_apm_var = tk.StringVar()
        self.current_eapm_var = tk.StringVar()
        self.peak_apm_var = tk.StringVar()
        self.peak_eapm_var = tk.StringVar()
        self.avg_apm_var = tk.StringVar()
        self.avg_eapm_var = tk.StringVar()
        
        ttk.Label(self.main_frame, textvariable=self.current_apm_var, font=font_large, foreground='blue').pack(pady=10)
        ttk.Label(self.main_frame, textvariable=self.current_eapm_var, font=font_large, foreground='green').pack(pady=10)
        ttk.Label(self.main_frame, textvariable=self.peak_apm_var).pack(pady=5)
        ttk.Label(self.main_frame, textvariable=self.peak_eapm_var).pack(pady=5)
        ttk.Label(self.main_frame, textvariable=self.avg_apm_var).pack(pady=5)
        ttk.Label(self.main_frame, textvariable=self.avg_eapm_var).pack(pady=5)

        ttk.Button(self.main_frame, text="Toggle Mini View", command=self.toggle_view).pack(pady=10)

    def setup_graph_frame(self):
        self.figure, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.apm_data = np.zeros(60)
        self.eapm_data = np.zeros(60)

        x = range(60)
        self.apm_bars = self.ax.bar(x, self.apm_data, color='blue', alpha=0.5, label='APM')
        self.eapm_bars = self.ax.bar(x, self.eapm_data, color='green', alpha=0.5, label='eAPM')

        self.ax.legend(loc='upper left')
        self.ax.set_title('APM and eAPM over time')
        self.ax.set_xlabel('Time (seconds ago)')
        self.ax.set_ylabel('Number of Actions')
        
        # Set fixed x and y axes
        self.ax.set_xlim(59, 0)
        self.ax.set_ylim(0, self.max_actions_per_second)
        self.ax.set_xticks([0, 15, 30, 45, 59])
        self.ax.set_xticklabels(['0', '15', '30', '45', '60'])
        self.ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=5))

        self.ani = animation.FuncAnimation(
            self.figure, 
            self.update_graph, 
            interval=1000, 
            blit=True, 
            save_count=100
        )

    def setup_settings_frame(self):
        try:
            ttk.Label(self.settings_frame, text="Transparency:").pack(pady=5)
            self.transparency_scale = ttk.Scale(self.settings_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL, command=self.update_transparency)
            self.transparency_scale.set(self.tracker.settings_manager.transparency)
            self.transparency_scale.pack(pady=5)

            ttk.Label(self.settings_frame, text="Target Program:").pack(pady=5)
            self.target_program_combobox = ttk.Combobox(self.settings_frame, values=self.tracker.settings_manager.window_list)
            self.target_program_combobox.set(self.tracker.settings_manager.target_program)
            self.target_program_combobox.pack(pady=5)
            ttk.Button(self.settings_frame, text="Set Target Program", command=self.set_target_program).pack(pady=5)
            ttk.Button(self.settings_frame, text="Clear Target Program", command=self.clear_target_program).pack(pady=5)
            ttk.Button(self.settings_frame, text="Refresh Window List", command=self.refresh_window_list).pack(pady=5)

            ttk.Label(self.settings_frame, text="Log Level:").pack(pady=5)
            self.log_level_combobox = ttk.Combobox(self.settings_frame, 
                values=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
            self.log_level_combobox.set(logging.getLevelName(self.tracker.settings_manager.log_level))
            self.log_level_combobox.pack(pady=5)
            ttk.Button(self.settings_frame, text="Set Log Level", command=self.set_log_level).pack(pady=5)

        except Exception as e:
            logging.error(f"Error setting up settings frame: {str(e)}")
            logging.debug(traceback.format_exc())
            raise

    def set_log_level(self):
        selected_level = self.log_level_combobox.get()
        if selected_level:
            self.tracker.settings_manager.set_log_level(selected_level)
            logging.info(f"Log level set to: {selected_level}")
        else:
            logging.warning("No log level selected")

    def update_transparency(self, value):
        alpha = float(value)
        if self.root:
            self.root.attributes('-alpha', alpha)
        if self.mini_window:
            self.mini_window.attributes('-alpha', alpha)

    def set_target_program(self):
        selected_window = self.target_program_combobox.get()
        if selected_window:
            self.tracker.settings_manager.set_target_program(selected_window)
            logging.info(f"Target program set to: {self.tracker.settings_manager.target_program}")
        else:
            logging.warning("No window selected")

    def clear_target_program(self):
        self.tracker.settings_manager.clear_target_program()
        self.target_program_combobox.set('')
        logging.info("Target program cleared")

    def refresh_window_list(self):
        self.tracker.settings_manager.update_window_list()
        self.target_program_combobox['values'] = self.tracker.settings_manager.window_list

    def update_gui(self):
        if not self.tracker.running:
            return

        current_apm = self.tracker.data_manager.calculate_current_apm()
        current_eapm = self.tracker.data_manager.calculate_current_eapm()
        avg_apm = self.tracker.data_manager.calculate_average_apm()
        avg_eapm = self.tracker.data_manager.calculate_average_eapm()

        self.current_apm_var.set(f"Current APM: {current_apm}")
        self.current_eapm_var.set(f"Current eAPM: {current_eapm}")
        self.tracker.data_manager.peak_apm = max(self.tracker.data_manager.peak_apm, current_apm)
        self.tracker.data_manager.peak_eapm = max(self.tracker.data_manager.peak_eapm, current_eapm)
        self.peak_apm_var.set(f"Peak APM: {self.tracker.data_manager.peak_apm}")
        self.peak_eapm_var.set(f"Peak eAPM: {self.tracker.data_manager.peak_eapm}")
        self.avg_apm_var.set(f"Average APM: {avg_apm:.2f}")
        self.avg_eapm_var.set(f"Average eAPM: {avg_eapm:.2f}")

        self.mini_apm_var.set(f"APM: {current_apm}")
        self.mini_eapm_var.set(f"eAPM: {current_eapm}")

        self.adjust_mini_view_size()

        self.root.after(1000 if self.is_mini_view else self.update_interval, self.update_gui)

    def update_graph(self, frame):
        current_time = self.tracker.data_manager.current_time()
        new_apm_data = np.zeros(60)
        new_eapm_data = np.zeros(60)

        for t in self.tracker.data_manager.actions:
            if current_time - t <= 60:
                index = int(current_time - t)
                if index < 60:
                    new_apm_data[index] += 1

        for t in self.tracker.data_manager.effective_actions:
            if current_time - t <= 60:
                index = int(current_time - t)
                if index < 60:
                    new_eapm_data[index] += 1

        # Clip the data to the maximum value
        np.clip(new_apm_data, 0, self.max_actions_per_second, out=new_apm_data)
        np.clip(new_eapm_data, 0, self.max_actions_per_second, out=new_eapm_data)

        # Update bar heights
        for rect, h in zip(self.apm_bars, new_apm_data):
            rect.set_height(h)
        for rect, h in zip(self.eapm_bars, new_eapm_data):
            rect.set_height(h)

        return self.apm_bars + self.eapm_bars

    def adjust_mini_view_size(self):
        self.mini_apm_label.update_idletasks()
        self.mini_eapm_label.update_idletasks()

        width = max(self.mini_apm_label.winfo_reqwidth(), self.mini_eapm_label.winfo_reqwidth())
        height = self.mini_apm_label.winfo_reqheight() + self.mini_eapm_label.winfo_reqheight()

        width += 10
        height += 10

        if (width, height) != self.last_mini_size:
            self.mini_window.geometry(f"{width}x{height}")
            self.last_mini_size = (width, height)

    def toggle_view(self, event=None):
        self.is_mini_view = not self.is_mini_view
        if self.is_mini_view:
            self.root.withdraw()
            self.mini_window.deiconify()
            if platform.system() == 'Windows':
                set_appwindow(self.mini_window)
        else:
            self.mini_window.withdraw()
            self.root.deiconify()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.mini_window.winfo_x() + deltax
        y = self.mini_window.winfo_y() + deltay
        self.mini_window.geometry(f"+{x}+{y}")

    def run_main_loop(self):
        if self.root:
            self.root.mainloop()
        else:
            logging.error("Error: Main window (root) is not initialized.")
