import threading
from pynput import keyboard, mouse
import win32gui
import win32process
import psutil
import logging

class InputManager:
    def __init__(self, tracker):
        self.tracker = tracker
        self.input_event = threading.Event()
        self.last_key = None

    def input_loop(self):
        def on_press(key):
            if self.is_target_program_active():
                self.tracker.on_action('keyboard')
                logging.debug(f"Keyboard action recorded for target program: {self.tracker.settings_manager.target_program}")

        def on_click(x, y, button, pressed):
            if pressed and self.is_target_program_active():
                self.tracker.on_action('mouse_click')
                logging.debug(f"Mouse click recorded for target program: {self.tracker.settings_manager.target_program}")

        def on_move(x, y):
            if self.is_target_program_active():
                self.tracker.on_action('selection')
                logging.debug(f"Mouse move recorded for target program: {self.tracker.settings_manager.target_program}")

        keyboard_listener = keyboard.Listener(on_press=on_press)
        mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)

        keyboard_listener.start()
        mouse_listener.start()

        while self.tracker.running:
            self.input_event.wait(1)  # Wait for 1 second or until set()
            self.input_event.clear()

        keyboard_listener.stop()
        mouse_listener.stop()

    def is_target_program_active(self):
        if not self.tracker.settings_manager.target_program:
            return True  # If no target program is set, track all inputs

        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            active_window = process.name().lower()
            target_program = self.tracker.settings_manager.target_program.lower()
            
            is_active = target_program in active_window
            logging.debug(f"Active window: {active_window}, Target program: {target_program}, Is active: {is_active}")
            return is_active
        except Exception as e:
            logging.error(f"Error checking active window: {e}")
            return False
