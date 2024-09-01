import keyboard
import mouse
import time
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from win32 import win32gui, win32process
import psutil
import threading
import array
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class RingBuffer:
    def __init__(self, size):
        self.max_size = size
        self.data = array.array('d', [0] * size)
        self.size = 0
        self.index = 0

    def append(self, value):
        if self.size < self.max_size:
            self.data[self.size] = value
            self.size += 1
        else:
            self.data[self.index] = value
            self.index = (self.index + 1) % self.max_size

    def get_all(self):
        return self.data[:self.size]

class APMTracker:
    def __init__(self):
        self.actions = RingBuffer(3600)  # Store actions for the last hour
        self.effective_actions = RingBuffer(3600)
        self.start_time = time.time()
        self.peak_apm = 0
        self.peak_eapm = 0
        self.running = True
        self.target_program = ""
        self.update_interval = 500  # milliseconds
        self.effective_threshold = 0.2  # 200ms
        self.last_action_time = 0
        self.graph_needs_update = True  # Track if the graph needs updating
        self.setup_gui()
        self.load_settings()
        self.input_thread = threading.Thread(target=self.input_loop, daemon=True)

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("APM Tracker")
        self.root.geometry("600x400")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        style = ttk.Style(self.root)
        style.theme_use('clam')  # Set a modern theme

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

        # Create mini-view
        self.mini_window = tk.Toplevel(self.root)
        self.mini_window.overrideredirect(True)
        self.mini_window.attributes('-topmost', True)
        # self.mini_window.configure(bg="#2c2c2c", padx=5, pady=5)  # Dark background with padding
        self.mini_window.geometry("90x65")  # Slightly larger for better spacing
        self.mini_window.withdraw()

        # Define a custom font
        custom_font = tkfont.Font(family="Segoe UI", size=12)  # Smaller font size for compactness

        # Create a frame to organize labels better
        mini_frame = ttk.Frame(self.mini_window, padding=(5, 5), style="Mini.TFrame")
        mini_frame.pack(expand=True, fill='both')

        # Labels with custom styling
        self.mini_apm_var = tk.StringVar()
        self.mini_eapm_var = tk.StringVar()

        tk.Label(mini_frame, textvariable=self.mini_apm_var, font=custom_font, fg="black").grid(row=0, column=0, sticky="w")
        tk.Label(mini_frame, textvariable=self.mini_eapm_var, font=custom_font, fg="black").grid(row=1, column=0, sticky="w")

        # Add dragging functionality to mini-view
        self.mini_window.bind('<ButtonPress-1>', self.start_move)
        self.mini_window.bind('<B1-Motion>', self.do_move)
        self.mini_window.bind('<Double-Button-1>', lambda e: self.toggle_view())

        self.is_mini_view = False

        # Set up hotkeys
        keyboard.add_hotkey('ctrl+shift+a', self.toggle_view)
        keyboard.add_hotkey('ctrl+shift+q', self.on_closing)


    def setup_main_frame(self):
        font_large = ("Helvetica", 24, 'bold')
        font_small = ("Helvetica", 12)

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

    def setup_settings_frame(self):
        ttk.Label(self.settings_frame, text="Transparency:").pack(pady=5)
        self.transparency_scale = ttk.Scale(self.settings_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL, command=self.update_transparency)
        self.transparency_scale.set(1.0)
        self.transparency_scale.pack(pady=5)

        ttk.Label(self.settings_frame, text="Target Program:").pack(pady=5)
        self.target_program_entry = ttk.Entry(self.settings_frame)
        self.target_program_entry.pack(pady=5)
        ttk.Button(self.settings_frame, text="Set Target Program", command=self.set_target_program).pack(pady=5)
        ttk.Button(self.settings_frame, text="Clear Target Program", command=self.clear_target_program).pack(pady=5)

    def update_transparency(self, value):
        alpha = float(value)
        self.root.attributes('-alpha', alpha)
        self.mini_window.attributes('-alpha', alpha)

    def set_target_program(self):
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        active_window = psutil.Process(pid).name()
        self.target_program_entry.delete(0, tk.END)
        self.target_program_entry.insert(0, active_window.lower())
        self.target_program = active_window.lower()

    def clear_target_program(self):
        self.target_program = ""
        self.target_program_entry.delete(0, tk.END)

    def save_settings(self):
        settings = {
            'target_program': self.target_program,
            'transparency': self.transparency_scale.get()
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.target_program = settings['target_program']
                self.transparency_scale.set(settings['transparency'])
        except FileNotFoundError:
            pass

    def on_action(self):
        current_time = time.time()

        if self.target_program:
            try:
                hwnd = win32gui.GetForegroundWindow()
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                active_window = psutil.Process(pid).name().lower()
                if active_window != self.target_program:
                    return
            except Exception:
                return

        self.actions.append(current_time)
        
        if current_time - self.last_action_time > self.effective_threshold:
            self.effective_actions.append(current_time)
            self.last_action_time = current_time

        self.graph_needs_update = True

    def input_loop(self):
        sleep_interval = 0.01
        keyboard.hook(lambda e: self.on_action())
        mouse.hook(lambda e: self.on_action() if e.event_type in ('down', 'click') else None)
        while self.running:
            time.sleep(sleep_interval)  
        keyboard.unhook_all()
        mouse.unhook_all()

    def calculate_current_apm(self):
        current_time = time.time()
        minute_ago = current_time - 60
        recent_actions = [t for t in self.actions.get_all() if t > minute_ago]
        return len(recent_actions)

    def calculate_current_eapm(self):
        current_time = time.time()
        minute_ago = current_time - 60
        recent_effective_actions = [t for t in self.effective_actions.get_all() if t > minute_ago]
        return len(recent_effective_actions)

    def calculate_average_apm(self):
        total_actions = len(self.actions.get_all())
        elapsed_time = (time.time() - self.start_time) / 60  # in minutes
        return total_actions / elapsed_time if elapsed_time > 0 else 0

    def calculate_average_eapm(self):
        total_effective_actions = len(self.effective_actions.get_all())
        elapsed_time = (time.time() - self.start_time) / 60  # in minutes
        return total_effective_actions / elapsed_time if elapsed_time > 0 else 0

    def update_graph(self, force_update=False):
        if not self.graph_needs_update and not force_update:
            return
        times = self.actions.get_all()
        effective_times = self.effective_actions.get_all()

        self.ax.clear()
        self.ax.hist(times, bins=60, color='blue', alpha=0.5, label='APM')
        self.ax.hist(effective_times, bins=60, color='green', alpha=0.5, label='eAPM')
        self.ax.legend(loc='upper right')
        self.ax.set_title('APM and eAPM over time')
        self.ax.set_xlabel('Time (seconds)')
        self.ax.set_ylabel('Number of Actions')

        self.canvas.draw()
        self.graph_needs_update = False

    def update_gui(self):
        if not self.running:
            return

        current_apm = self.calculate_current_apm()
        current_eapm = self.calculate_current_eapm()
        avg_apm = self.calculate_average_apm()
        avg_eapm = self.calculate_average_eapm()

        self.current_apm_var.set(f"Current APM: {current_apm}")
        self.current_eapm_var.set(f"Current eAPM: {current_eapm}")
        self.peak_apm = max(self.peak_apm, current_apm)
        self.peak_eapm = max(self.peak_eapm, current_eapm)
        self.peak_apm_var.set(f"Peak APM: {self.peak_apm}")
        self.peak_eapm_var.set(f"Peak eAPM: {self.peak_eapm}")
        self.avg_apm_var.set(f"Average APM: {avg_apm:.2f}")
        self.avg_eapm_var.set(f"Average eAPM: {avg_eapm:.2f}")

        # Update the mini view
        self.mini_apm_var.set(f"APM: {current_apm}")
        self.mini_eapm_var.set(f"eAPM: {current_eapm}")

        self.update_graph()

        # Only update every 1 second in mini-view to reduce load
        self.root.after(1000 if self.is_mini_view else self.update_interval, self.update_gui)

    def toggle_view(self):
        self.is_mini_view = not self.is_mini_view
        if self.is_mini_view:
            self.root.withdraw()
            self.mini_window.deiconify()
        else:
            self.mini_window.withdraw()
            self.root.deiconify()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = event.x_root - self.x
        y = event.y_root - self.y
        self.mini_window.geometry(f"+{x}+{y}")

    def on_closing(self):
        self.save_settings()
        self.running = False
        self.input_thread.join()
        self.root.quit()

    def run(self):
        self.input_thread.start()
        self.update_gui()
        self.root.mainloop()

if __name__ == "__main__":
    tracker = APMTracker()
    tracker.run()
