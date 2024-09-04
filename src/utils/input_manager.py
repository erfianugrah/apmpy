import threading
from pynput import keyboard, mouse
import win32gui
import win32process
import psutil
import logging
from utils.constants import INPUT_EVENT_WAIT_TIME

class InputManager:
    def __init__(self, tracker):
        self.tracker = tracker
        self.input_event = threading.Event()
        self.last_key = None
        self.target_pid = None

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
        if not self.tracker.settings_manager.target_program:
            return True

        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            if self.target_pid != pid:
                self.target_pid = pid
                process = psutil.Process(pid)
                active_window = process.name().lower()
                target_program = self.tracker.settings_manager.target_program.lower()
                return target_program in active_window
            return True
        except Exception as e:
            logging.error(f"Error checking active window: {e}")
            return False
