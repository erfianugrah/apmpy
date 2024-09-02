import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import logging
from utils import get_icon_path, set_window_icon, set_appwindow
import platform
import numpy as np
import traceback

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

        self.apm_data = np.zeros(self.tracker.settings_manager.graph_time_range)
        self.eapm_data = np.zeros(self.tracker.settings_manager.graph_time_range)

        x = range(self.tracker.settings_manager.graph_time_range)
        self.apm_bars = self.ax.bar(x, self.apm_data, color='blue', alpha=0.5, label='APM')
        self.eapm_bars = self.ax.bar(x, self.eapm_data, color='green', alpha=0.5, label='eAPM')

        self.ax.legend(loc='upper left')
        self.ax.set_title('APM and eAPM over time')
        self.ax.set_xlabel('Time (seconds ago)')
        self.ax.set_ylabel('Number of Actions')
        
        self.ax.set_xlim(self.tracker.settings_manager.graph_time_range - 1, 0)
        self.ax.set_ylim(0, self.tracker.settings_manager.max_actions_per_second)
        self.ax.set_xticks([0, self.tracker.settings_manager.graph_time_range // 4, self.tracker.settings_manager.graph_time_range // 2, 3 * self.tracker.settings_manager.graph_time_range // 4, self.tracker.settings_manager.graph_time_range - 1])
        self.ax.set_xticklabels(['0', str(self.tracker.settings_manager.graph_time_range // 4), str(self.tracker.settings_manager.graph_time_range // 2), str(3 * self.tracker.settings_manager.graph_time_range // 4), str(self.tracker.settings_manager.graph_time_range)])
        self.ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=5))

        self.ani = animation.FuncAnimation(
            self.figure, 
            self.update_graph, 
            interval=self.tracker.settings_manager.graph_update_interval, 
            blit=True, 
            save_count=100
        )

    def setup_settings_frame(self):
        try:
            # Create a canvas that fills the entire frame
            canvas = tk.Canvas(self.settings_frame)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Add a scrollbar to the canvas
            scrollbar = ttk.Scrollbar(self.settings_frame, orient=tk.VERTICAL, command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Configure the canvas
            canvas.configure(yscrollcommand=scrollbar.set)

            # Create another frame inside the canvas
            inner_frame = ttk.Frame(canvas)

            # Add that frame to a window in the canvas
            canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

            # Configure canvas and inner_frame
            def configure_inner_frame(event):
                # Update the width of the inner frame to match the canvas
                canvas.itemconfig(canvas_window, width=event.width)
                
            canvas.bind('<Configure>', configure_inner_frame)

            def on_frame_configure(event):
                # Reset the scroll region to encompass the inner frame
                canvas.configure(scrollregion=canvas.bbox("all"))

            inner_frame.bind('<Configure>', on_frame_configure)

            # Bind mousewheel to scrolling only when the mouse is over the canvas
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            def _bind_mousewheel(event):
                canvas.bind_all("<MouseWheel>", _on_mousewheel)

            def _unbind_mousewheel(event):
                canvas.unbind_all("<MouseWheel>")

            canvas.bind('<Enter>', _bind_mousewheel)
            canvas.bind('<Leave>', _unbind_mousewheel)

            center_frame = ttk.Frame(inner_frame)
            center_frame.pack(expand=True)

            ttk.Label(center_frame, text="Transparency:").pack(pady=5, padx=10, anchor="w")
            self.transparency_scale = ttk.Scale(center_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL, command=self.update_transparency)
            self.transparency_scale.set(self.tracker.settings_manager.transparency)
            self.transparency_scale.pack(pady=5, padx=10, fill="x")

            ttk.Label(center_frame, text="Target Program:").pack(pady=5, padx=10, anchor="w")
            self.target_program_combobox = ttk.Combobox(center_frame, values=self.tracker.settings_manager.window_list)
            self.target_program_combobox.set(self.tracker.settings_manager.target_program)
            self.target_program_combobox.pack(pady=5, padx=10, fill="x")
            ttk.Button(center_frame, text="Set Target Program", command=self.set_target_program).pack(pady=5, padx=10)
            ttk.Button(center_frame, text="Clear Target Program", command=self.clear_target_program).pack(pady=5, padx=10)
            ttk.Button(center_frame, text="Refresh Window List", command=self.refresh_window_list).pack(pady=5, padx=10)

            ttk.Label(center_frame, text="Log Level:").pack(pady=5, padx=10, anchor="w")
            self.log_level_combobox = ttk.Combobox(center_frame, 
                values=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
            self.log_level_combobox.set(logging.getLevelName(self.tracker.settings_manager.log_level))
            self.log_level_combobox.pack(pady=5, padx=10, fill="x")
            ttk.Button(center_frame, text="Set Log Level", command=self.set_log_level).pack(pady=5, padx=10)

            ttk.Label(center_frame, text="Update Interval (ms):").pack(pady=5, padx=10, anchor="w")
            self.update_interval_entry = ttk.Entry(center_frame)
            self.update_interval_entry.insert(0, str(self.tracker.settings_manager.update_interval))
            self.update_interval_entry.pack(pady=5, padx=10, fill="x")

            ttk.Label(center_frame, text="Graph Update Interval (ms):").pack(pady=5, padx=10, anchor="w")
            self.graph_update_interval_entry = ttk.Entry(center_frame)
            self.graph_update_interval_entry.insert(0, str(self.tracker.settings_manager.graph_update_interval))
            self.graph_update_interval_entry.pack(pady=5, padx=10, fill="x")

            ttk.Label(center_frame, text="Graph Time Range:").pack(pady=5, padx=10, anchor="w")
            self.graph_time_range_var = tk.StringVar()
            self.graph_time_range_combobox = ttk.Combobox(center_frame, 
                textvariable=self.graph_time_range_var,
                values=[f"{t} seconds" for t in self.tracker.settings_manager.graph_time_range_options])
            self.graph_time_range_combobox.set(f"{self.tracker.settings_manager.graph_time_range} seconds")
            self.graph_time_range_combobox.pack(pady=5, padx=10, fill="x")
            self.graph_time_range_combobox.bind("<<ComboboxSelected>>", self.on_graph_time_range_change)

            ttk.Label(center_frame, text="Max Actions Per Second:").pack(pady=5, padx=10, anchor="w")
            self.max_actions_per_second_entry = ttk.Entry(center_frame)
            self.max_actions_per_second_entry.insert(0, str(self.tracker.settings_manager.max_actions_per_second))
            self.max_actions_per_second_entry.pack(pady=5, padx=10, fill="x")

            ttk.Label(center_frame, text="Action Cooldown (ms):").pack(pady=5, padx=10, anchor="w")
            self.action_cooldown_entry = ttk.Entry(center_frame)
            self.action_cooldown_entry.insert(0, str(int(self.tracker.settings_manager.action_cooldown * 1000)))
            self.action_cooldown_entry.pack(pady=5, padx=10, fill="x")

            ttk.Label(center_frame, text="Effective Action Cooldown (ms):").pack(pady=5, padx=10, anchor="w")
            self.eaction_cooldown_entry = ttk.Entry(center_frame)
            self.eaction_cooldown_entry.insert(0, str(int(self.tracker.settings_manager.eapm_cooldown * 1000)))
            self.eaction_cooldown_entry.pack(pady=5, padx=10, fill="x")

            ttk.Button(center_frame, text="Apply Settings", command=self.apply_settings).pack(pady=10, padx=10)

            # Update the scrollregion when all widgets are in place
            inner_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

        except Exception as e:
            logging.error(f"Error setting up settings frame: {str(e)}")
            logging.debug(traceback.format_exc())
            raise    

    def on_graph_time_range_change(self, event):
        selected = self.graph_time_range_var.get()
        time_range = int(selected.split()[0])
        index = self.tracker.settings_manager.graph_time_range_options.index(time_range)
        self.tracker.settings_manager.set_graph_time_range(index)
        self.update_graph_settings()

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

    def set_log_level(self):
        selected_level = self.log_level_combobox.get()
        if selected_level:
            self.tracker.settings_manager.set_log_level(selected_level)
            logging.info(f"Log level set to: {selected_level}")
        else:
            logging.warning("No log level selected")

    def apply_settings(self):
        try:
            new_settings = {
                'update_interval': int(self.update_interval_entry.get()),
                'graph_update_interval': int(self.graph_update_interval_entry.get()),
                'max_actions_per_second': int(self.max_actions_per_second_entry.get()),
                'action_cooldown': int(self.action_cooldown_entry.get()) / 1000,
                'eapm_cooldown': int(self.eaction_cooldown_entry.get()) / 1000
            }
            self.tracker.settings_manager.update_settings(**new_settings)
            self.update_graph_settings()
            logging.info("Settings applied successfully")
            messagebox.showinfo("Success", "Settings applied successfully")
        except ValueError as e:
            logging.error(f"Invalid input in settings: {str(e)}")
            messagebox.showerror("Error", "Please enter valid numbers for all settings.")
        except Exception as e:
            logging.error(f"Error applying settings: {str(e)}")
            logging.debug(traceback.format_exc())
            messagebox.showerror("Error", f"An error occurred while applying settings: {str(e)}")

    def update_graph_settings(self):
        # Update graph based on new settings
        self.ax.clear()
        x = range(self.tracker.settings_manager.graph_time_range)
        self.apm_data = np.zeros(self.tracker.settings_manager.graph_time_range)
        self.eapm_data = np.zeros(self.tracker.settings_manager.graph_time_range)
        self.apm_bars = self.ax.bar(x, self.apm_data, color='blue', alpha=0.5, label='APM')
        self.eapm_bars = self.ax.bar(x, self.eapm_data, color='green', alpha=0.5, label='eAPM')

        self.ax.legend(loc='upper left')
        self.ax.set_title('APM and eAPM over time')
        self.ax.set_xlabel('Time (seconds ago)')
        self.ax.set_ylabel('Number of Actions')
        
        self.ax.set_xlim(self.tracker.settings_manager.graph_time_range - 1, 0)
        self.ax.set_ylim(0, self.tracker.settings_manager.max_actions_per_second)
        self.ax.set_xticks([0, self.tracker.settings_manager.graph_time_range // 2, self.tracker.settings_manager.graph_time_range - 1])
        self.ax.set_xticklabels(['0', str(self.tracker.settings_manager.graph_time_range // 2), str(self.tracker.settings_manager.graph_time_range)])
        self.ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=5))

        self.canvas.draw()

    def update_gui_elements(self):
        self.setup_graph_frame()
        self.root.after_cancel(self.update_job)
        self.update_gui()

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

            self.update_job = self.root.after(self.tracker.settings_manager.update_interval, self.update_gui)

    def update_graph(self, frame):
        current_time = self.tracker.data_manager.current_time()
        new_apm_data = np.zeros(self.tracker.settings_manager.graph_time_range)
        new_eapm_data = np.zeros(self.tracker.settings_manager.graph_time_range)

        for t in self.tracker.data_manager.actions:
            if current_time - t <= self.tracker.settings_manager.graph_time_range:
                index = int(current_time - t)
                if index < self.tracker.settings_manager.graph_time_range:
                    new_apm_data[index] += 1

        for t in self.tracker.data_manager.effective_actions:
            if current_time - t <= self.tracker.settings_manager.graph_time_range:
                index = int(current_time - t)
                if index < self.tracker.settings_manager.graph_time_range:
                    new_eapm_data[index] += 1

        # Update bar heights
        for rect, h in zip(self.apm_bars, new_apm_data):
            rect.set_height(h)
        for rect, h in zip(self.eapm_bars, new_eapm_data):
            rect.set_height(h)

        # Dynamically adjust y-axis
        max_value = max(np.max(new_apm_data), np.max(new_eapm_data))
        y_max = min(max(max_value * 1.1, 1), self.tracker.settings_manager.max_actions_per_second)
        self.ax.set_ylim(0, y_max)

        # Update y-axis ticks
        self.ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=5))

        # Force redraw of the figure
        self.figure.canvas.draw()

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
            self.update_gui()
            self.root.mainloop()
        else:
            logging.error("Error: Main window (root) is not initialized.")
