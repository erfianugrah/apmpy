import keyboard
import mouse
import time
import tkinter as tk
from tkinter import ttk
from win32 import win32gui, win32process
import psutil
import threading
import array

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
        self.start_time = time.time()
        self.peak_apm = 0
        self.running = True
        self.target_program = ""
        self.update_interval = 500  # milliseconds
        self.setup_gui()
        self.input_thread = threading.Thread(target=self.input_loop, daemon=True)
        self.matplotlib_loaded = False

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("APM Tracker")
        self.root.geometry("600x400")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
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
        self.mini_window.geometry("120x30")
        self.mini_apm_var = tk.StringVar()
        self.mini_label = tk.Label(self.mini_window, textvariable=self.mini_apm_var, 
                                   font=("Helvetica", 16), bg='white', fg='black')
        self.mini_label.pack(fill=tk.BOTH, expand=True)
        self.mini_window.withdraw()

        # Add dragging functionality to mini-view
        self.mini_label.bind('<ButtonPress-1>', self.start_move)
        self.mini_label.bind('<B1-Motion>', self.do_move)
        self.mini_label.bind('<Double-Button-1>', lambda e: self.toggle_view())

        self.is_mini_view = False

    def setup_main_frame(self):
        self.current_apm_var = tk.StringVar()
        self.peak_apm_var = tk.StringVar()
        self.avg_apm_var = tk.StringVar()
        
        ttk.Label(self.main_frame, textvariable=self.current_apm_var, font=("Helvetica", 24)).pack(pady=10)
        ttk.Label(self.main_frame, textvariable=self.peak_apm_var).pack(pady=5)
        ttk.Label(self.main_frame, textvariable=self.avg_apm_var).pack(pady=5)

        ttk.Button(self.main_frame, text="Toggle Mini View", command=self.toggle_view).pack(pady=10)

    def setup_graph_frame(self):
        self.graph_label = ttk.Label(self.graph_frame, text="Graph loading...")
        self.graph_label.pack(pady=20)
        self.root.after(100, self.load_matplotlib)

    def load_matplotlib(self):
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.draw()
        self.graph_label.pack_forget()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.matplotlib_loaded = True

    def setup_settings_frame(self):
        ttk.Label(self.settings_frame, text="Target Program:").pack(pady=5)
        self.target_program_entry = ttk.Entry(self.settings_frame)
        self.target_program_entry.pack(pady=5)
        ttk.Button(self.settings_frame, text="Set Target Program", command=self.set_target_program).pack(pady=5)
        ttk.Button(self.settings_frame, text="Clear Target Program", command=self.clear_target_program).pack(pady=5)

    def set_target_program(self):
        self.target_program = self.target_program_entry.get().lower()

    def clear_target_program(self):
        self.target_program = ""
        self.target_program_entry.delete(0, tk.END)

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

    def input_loop(self):
        keyboard.hook(lambda e: self.on_action())
        mouse.hook(lambda e: self.on_action() if e.event_type in ('down', 'click') else None)
        while self.running:
            time.sleep(0.001)  # Small sleep to prevent CPU hogging
        keyboard.unhook_all()
        mouse.unhook_all()

    def calculate_current_apm(self):
        current_time = time.time()
        minute_ago = current_time - 60
        recent_actions = [t for t in self.actions.get_all() if t > minute_ago]
        return len(recent_actions)

    def calculate_average_apm(self):
        total_actions = self.actions.size
        elapsed_time = (time.time() - self.start_time) / 60  # in minutes
        return total_actions / elapsed_time if elapsed_time > 0 else 0

    def update_gui(self):
        if not self.running:
            return

        current_apm = self.calculate_current_apm()
        avg_apm = self.calculate_average_apm()

        self.current_apm_var.set(f"Current APM: {current_apm}")
        self.mini_apm_var.set(f"APM: {current_apm}")
        self.peak_apm = max(self.peak_apm, current_apm)
        self.peak_apm_var.set(f"Peak APM: {self.peak_apm}")
        self.avg_apm_var.set(f"Average APM: {avg_apm:.2f}")

        if self.matplotlib_loaded:
            self.update_graph()
        
        self.root.after(self.update_interval, self.update_gui)

    def update_graph(self):
        self.ax.clear()
        times = [t - time.time() for t in self.actions.get_all()]
        self.ax.hist(times, bins=60, range=(-60, 0))
        self.ax.set_title("APM Last 60 Seconds")
        self.ax.set_xlabel("Seconds Ago")
        self.ax.set_ylabel("Actions")
        self.canvas.draw()

    def toggle_view(self):
        if self.is_mini_view:
            self.mini_window.withdraw()
            self.root.deiconify()
        else:
            self.root.withdraw()
            self.mini_window.deiconify()
        self.is_mini_view = not self.is_mini_view

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.mini_window.winfo_x() + deltax
        y = self.mini_window.winfo_y() + deltay
        self.mini_window.geometry(f"+{x}+{y}")

    def on_closing(self):
        self.running = False
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.input_thread.start()
        print("APM Tracker started. Close the window to exit.")
        self.update_gui()
        self.root.mainloop()
        self.input_thread.join()

if __name__ == "__main__":
    tracker = APMTracker()
    tracker.run()
