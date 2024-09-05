import threading
from pynput import keyboard, mouse
import psutil
import logging
import time
import os
import subprocess
from utils.constants import INPUT_EVENT_WAIT_TIME

class InputManager:
    def __init__(self, tracker):
        self.tracker = tracker
        self.input_event = threading.Event()
        self.last_key = None
        self.last_active_check = 0
        self.last_active_state = True
        self.active_check_interval = 1.0  # Check active window every 1 second

    def input_loop(self):
        def on_press(key):
            if self.is_target_program_active():
                self.tracker.on_action('keyboard')

        def on_click(x, y, button, pressed):
            if pressed and self.is_target_program_active():
                self.tracker.on_action('mouse_click')

        keyboard_listener = keyboard.Listener(on_press=on_press)
        mouse_listener = mouse.Listener(on_click=on_click)

        keyboard_listener.start()
        mouse_listener.start()

        while self.tracker.running:
            self.input_event.wait(INPUT_EVENT_WAIT_TIME)
            self.input_event.clear()

        keyboard_listener.stop()
        mouse_listener.stop()

    def is_target_program_active(self):
        current_time = time.time()
        if current_time - self.last_active_check < self.active_check_interval:
            return self.last_active_state

        self.last_active_check = current_time
        if not self.tracker.settings_manager.target_program:
            self.last_active_state = True
            return True

        try:
            if os.name == 'nt':  # Windows
                self.last_active_state = self._check_active_window_windows()
            elif os.name == 'posix':  # Linux
                self.last_active_state = self._check_active_window_linux()
            else:
                logging.error("Unsupported operating system")
                self.last_active_state = False
            return self.last_active_state
        except Exception as e:
            logging.error(f"Error checking active window: {e}")
            self.last_active_state = False
            return False

    def _check_active_window_windows(self):
        import win32gui
        import win32process
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        active_window = process.name().lower()
        target_program = self.tracker.settings_manager.target_program.lower()
        return target_program in active_window

    def _check_active_window_linux(self):
        try:
            active_window = subprocess.check_output(['xdotool', 'getactivewindow', 'getwindowname']).decode().strip().lower()
            target_program = self.tracker.settings_manager.target_program.lower()
            return target_program in active_window
        except subprocess.CalledProcessError:
            logging.error("Error getting active window name on Linux")
            return False
