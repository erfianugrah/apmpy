import time
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from tkinter import PhotoImage
import psutil
import threading
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import os
import sys
from collections import deque
import platform
import win32gui
import win32con
import win32process
from pynput import keyboard, mouse
from PIL import Image, ImageTk
import logging
import traceback

# Set up logging
logging.basicConfig(filename='apm_tracker.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
class APMTracker:
    def __init__(self):
        self.actions = deque(maxlen=3600)  # Store actions for the last hour
        self.effective_actions = deque(maxlen=3600)
        self.last_action_time = 0
        self.action_cooldown = 0.05  # 50ms cooldown between actions
        self.eapm_cooldown = 0.5  # 500ms cooldown for eAPM
        self.last_eapm_action_time = 0
        self.last_action_type = None
        self.start_time = time.time()
        self.peak_apm = 0
        self.peak_eapm = 0
        self.running = True
        self.target_program = ""
        self.update_interval = 500  # milliseconds
        self.graph_needs_update = True
        self.bg_color = '#F5F5F5'  # Off-white background color
        self.last_mini_size = (0, 0)  # Store last mini-view size
        self.input_event = threading.Event()
        self.root = None
        self.mini_window = None
        self.icon_path = self.get_icon_path()        
        self.window_list = []
        self.window_list = []

        try:
            self.update_window_list()
        except Exception as e:
            logging.error(f"Error initializing window list: {str(e)}")
            logging.debug(traceback.format_exc())

    def get_icon_path(self):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, 'icons', 'keebfire.png')
        if os.path.exists(icon_path):
            return icon_path
        return None

    def set_window_icon(self, window):
        if self.icon_path:
            try:
                icon = PhotoImage(file=self.icon_path)
                window.iconphoto(True, icon)
                print(f"Icon set successfully for {window.title()}")
            except Exception as e:
                print(f"Error setting icon: {e}")
        else:
            print("Icon file not found.")

    def on_action(self, action_type):
        try:
            current_time = time.time()

            if self.target_program:
                try:
                    if platform.system() == 'Windows':
                        import win32gui
                        hwnd = win32gui.GetForegroundWindow()
                        active_window = win32gui.GetWindowText(hwnd).lower()
                    else:
                        active_window = os.popen('xdotool getwindowfocus getwindowname').read().strip().lower()
                    
                    if active_window != self.target_program:
                        return
                except Exception as e:
                    logging.error(f"Error checking active window: {str(e)}")
                    logging.debug(traceback.format_exc())
                    return

            # Rest of the method remains the same
            # ... (previous on_action code)
        except Exception as e:
            logging.error(f"Error in on_action: {str(e)}")
            logging.debug(traceback.format_exc())

        # APM calculation (only keystrokes and mouse clicks)
        if action_type in ['keyboard', 'mouse_click']:
            if current_time - self.last_action_time >= self.action_cooldown:
                self.actions.append(current_time)
                self.last_action_time = current_time

        # Strict eAPM calculation
        if self.is_effective_action(action_type, current_time):
            self.effective_actions.append(current_time)
            self.last_eapm_action_time = current_time
            self.last_action_type = action_type

        self.graph_needs_update = True
        self.input_event.set()  # Signal that an action occurred

    def is_effective_action(self, action_type, current_time):
        if (current_time - self.last_eapm_action_time < self.eapm_cooldown or
            action_type == self.last_action_type):
            return False

        if action_type in ['keyboard', 'mouse_click']:
            return True
        elif action_type == 'selection' and self.last_action_type != 'selection':
            return True

        return False

    def setup_gui(self):
        self.root = tk.Tk()
        self.set_window_icon(self.root)  # Set icon immediately after creating the window
        self.root.title("APM Tracker")
        self.root.geometry("600x400")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Attempt to set the icon again after a short delay
        self.root.after(100, lambda: self.set_window_icon(self.root))

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

        # Define custom font
        self.custom_font = tkfont.Font(family="Segoe UI", size=12)
        
        # Create mini-view
        self.create_mini_window()

    def create_mini_window(self):
        # Create mini-view
        self.mini_window = tk.Toplevel(self.root)
        self.mini_window.title("APM Tracker Mini")
        self.mini_window.geometry("150x70")  # Set initial size
        self.mini_window.attributes('-topmost', True)
        self.mini_window.withdraw()  # Initially hide the mini-view

        # Set icon for mini-view
        self.set_window_icon(self.mini_window)

        # Attempt to set the icon again after a short delay
        self.mini_window.after(100, lambda: self.set_window_icon(self.mini_window))

        # Remove window decorations but keep it detectable
        self.mini_window.overrideredirect(True)

        # Create a frame to organize labels
        self.mini_frame = tk.Frame(self.mini_window, bg=self.bg_color)
        self.mini_frame.pack(expand=True, fill='both')

        # Labels with custom styling
        self.mini_apm_var = tk.StringVar()
        self.mini_eapm_var = tk.StringVar()

        self.mini_apm_label = tk.Label(self.mini_frame, textvariable=self.mini_apm_var, font=self.custom_font, bg=self.bg_color)
        self.mini_apm_label.pack(anchor='w', padx=5, pady=2)
        self.mini_eapm_label = tk.Label(self.mini_frame, textvariable=self.mini_eapm_var, font=self.custom_font, bg=self.bg_color)
        self.mini_eapm_label.pack(anchor='w', padx=5, pady=2)

        # Add dragging functionality to mini-view
        self.mini_window.bind('<ButtonPress-1>', self.start_move)
        self.mini_window.bind('<B1-Motion>', self.do_move)
        self.mini_window.bind('<Double-Button-1>', self.toggle_view)

        self.is_mini_view = False

    def set_appwindow(self, root):
        hwnd = win32gui.GetParent(root.winfo_id())
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        style = style & ~win32con.WS_EX_TOOLWINDOW
        style = style | win32con.WS_EX_APPWINDOW
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
        root.wm_withdraw()
        root.after(10, lambda: root.wm_deiconify())

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

        # Initialize with 60 empty bars
        self.apm_data = [0] * 60
        self.eapm_data = [0] * 60

        # Create bar containers
        x = range(60)
        self.apm_bars = self.ax.bar(x, self.apm_data, color='blue', alpha=0.5, label='APM')
        self.eapm_bars = self.ax.bar(x, self.eapm_data, color='green', alpha=0.5, label='eAPM')

        self.ax.legend(loc='upper left')
        self.ax.set_title('APM and eAPM over time')
        self.ax.set_xlabel('Time (seconds ago)')
        self.ax.set_ylabel('Number of Actions')
        
        # Set x-axis to represent seconds ago, with 0 on the right
        self.ax.set_xlim(59, 0)
        self.ax.set_xticks([0, 15, 30, 45, 59])
        self.ax.set_xticklabels(['0', '15', '30', '45', '60'])

        self.ani = animation.FuncAnimation(
            self.figure, 
            self.update_graph, 
            interval=1000, 
            blit=False, 
            save_count=100
        )

    def setup_settings_frame(self):
        try:
            ttk.Label(self.settings_frame, text="Transparency:").pack(pady=5)
            self.transparency_scale = ttk.Scale(self.settings_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL, command=self.update_transparency)
            self.transparency_scale.set(1.0)
            self.transparency_scale.pack(pady=5)

            ttk.Label(self.settings_frame, text="Target Program:").pack(pady=5)
            self.target_program_combobox = ttk.Combobox(self.settings_frame, values=self.window_list)
            self.target_program_combobox.pack(pady=5)
            ttk.Button(self.settings_frame, text="Set Target Program", command=self.set_target_program).pack(pady=5)
            ttk.Button(self.settings_frame, text="Clear Target Program", command=self.clear_target_program).pack(pady=5)
            ttk.Button(self.settings_frame, text="Refresh Window List", command=self.update_window_list).pack(pady=5)
        except Exception as e:
            logging.error(f"Error setting up settings frame: {str(e)}")
            logging.debug(traceback.format_exc())
            raise

    def update_transparency(self, value):
        alpha = float(value)
        if self.root:
            self.root.attributes('-alpha', alpha)
        if self.mini_window:
            self.mini_window.attributes('-alpha', alpha)

    def update_window_list(self):
        try:
            self.window_list.clear()
            if platform.system() == 'Windows':
                import win32gui
                def enum_window_callback(hwnd, window_list):
                    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                        window_list.append(win32gui.GetWindowText(hwnd))
                win32gui.EnumWindows(enum_window_callback, self.window_list)
            else:
                # For non-Windows systems
                self.window_list = os.popen("wmctrl -l | awk '{$1=$2=$3=""; print $0}'").read().splitlines()

            # Update the combobox values
            if hasattr(self, 'target_program_combobox'):
                self.target_program_combobox['values'] = self.window_list
            logging.info(f"Updated window list with {len(self.window_list)} items")
        except Exception as e:
            logging.error(f"Error updating window list: {str(e)}")
            logging.debug(traceback.format_exc())

    def set_target_program(self):
        try:
            selected_window = self.target_program_combobox.get()
            if selected_window:
                self.target_program = selected_window.lower()
                logging.info(f"Target program set to: {self.target_program}")
            else:
                logging.warning("No window selected")
        except Exception as e:
            logging.error(f"Error setting target program: {str(e)}")
            logging.debug(traceback.format_exc())

    def clear_target_program(self):
        try:
            self.target_program = ""
            self.target_program_combobox.set('')
            logging.info("Target program cleared")
        except Exception as e:
            logging.error(f"Error clearing target program: {str(e)}")
            logging.debug(traceback.format_exc())

    def save_settings(self):
        settings = {
            'target_program': self.target_program,
            'transparency': self.transparency_scale.get()
        }
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
        except IOError as e:
            print(f"Error saving settings: {e}")

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.target_program = settings.get('target_program', '')
                self.transparency_scale.set(settings.get('transparency', 1.0))
        except FileNotFoundError:
            print("Settings file not found. Using defaults.")
        except json.JSONDecodeError:
            print("Error decoding settings file. Using defaults.")

    def input_loop(self):
        def on_press(key):
            self.on_action('keyboard')

        def on_click(x, y, button, pressed):
            if pressed:
                self.on_action('mouse_click')

        def on_move(x, y):
            self.on_action('selection')

        keyboard_listener = keyboard.Listener(on_press=on_press)
        mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)

        keyboard_listener.start()
        mouse_listener.start()

        while self.running:
            self.input_event.wait(1)  # Wait for 1 second or until set()
            self.input_event.clear()

        keyboard_listener.stop()
        mouse_listener.stop()

    def calculate_current_apm(self):
        current_time = time.time()
        minute_ago = current_time - 60
        recent_actions = [t for t in self.actions if t > minute_ago]
        return len(recent_actions)

    def calculate_current_eapm(self):
        current_time = time.time()
        minute_ago = current_time - 60
        recent_effective_actions = [t for t in self.effective_actions if t > minute_ago]
        return len(recent_effective_actions)

    def calculate_average_apm(self):
        total_actions = len(self.actions)
        elapsed_time = (time.time() - self.start_time) / 60  # in minutes
        return total_actions / elapsed_time if elapsed_time > 0 else 0

    def calculate_average_eapm(self):
        total_effective_actions = len(self.effective_actions)
        elapsed_time = (time.time() - self.start_time) / 60  # in minutes
        return total_effective_actions / elapsed_time if elapsed_time > 0 else 0

    def update_graph(self, frame):
        current_time = time.time()
        apm_data = [0] * 60
        eapm_data = [0] * 60

        for t in self.actions:
            if current_time - t <= 60:
                index = int(current_time - t)
                if index < 60:
                    apm_data[index] += 1

        for t in self.effective_actions:
            if current_time - t <= 60:
                index = int(current_time - t)
                if index < 60:
                    eapm_data[index] += 1

        # Update the heights of the bars
        for rect, h in zip(self.apm_bars, apm_data):
            rect.set_height(h)
        for rect, h in zip(self.eapm_bars, eapm_data):
            rect.set_height(h)

        self.ax.relim()
        self.ax.autoscale_view()

        return self.apm_bars + self.eapm_bars

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

        # Adjust mini-view size based on content
        self.adjust_mini_view_size()

        # Only update every 1 second in mini-view to reduce load
        self.root.after(1000 if self.is_mini_view else self.update_interval, self.update_gui)

    def adjust_mini_view_size(self):
        # Update the label sizes
        self.mini_apm_label.update_idletasks()
        self.mini_eapm_label.update_idletasks()

        # Calculate the required width and height
        width = max(self.mini_apm_label.winfo_reqwidth(), self.mini_eapm_label.winfo_reqwidth())
        height = self.mini_apm_label.winfo_reqheight() + self.mini_eapm_label.winfo_reqheight()

        # Add some padding
        width += 10
        height += 10

        # Only update if the size has changed
        if (width, height) != self.last_mini_size:
            self.mini_window.geometry(f"{width}x{height}")
            self.last_mini_size = (width, height)

    def toggle_view(self, event=None):
        self.is_mini_view = not self.is_mini_view
        if self.is_mini_view:
            self.root.withdraw()
            self.mini_window.deiconify()
            if platform.system() == 'Windows':
                self.set_appwindow(self.mini_window)
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

    def on_closing(self):
        self.save_settings()
        self.running = False
        self.input_event.set()  # Ensure input_loop exits
        self.input_thread.join()
        self.root.quit()

    def run(self):
        try:
            self.setup_gui()
            self.load_settings()
            self.input_thread = threading.Thread(target=self.input_loop, daemon=True)
            self.input_thread.start()
            self.update_gui()
            if self.mini_window:
                self.mini_window.withdraw()
            if self.root:
                self.root.mainloop()
            else:
                logging.error("Error: Main window (root) is not initialized.")
        except Exception as e:
            logging.error(f"Error in run method: {str(e)}")
            logging.debug(traceback.format_exc())
            raise

if __name__ == "__main__":
    try:
        tracker = APMTracker()
        tracker.run()
    except Exception as e:
        logging.critical(f"Critical error in main: {str(e)}")
        logging.debug(traceback.format_exc())
        print(f"A critical error occurred. Please check the log file for details: {str(e)}")
