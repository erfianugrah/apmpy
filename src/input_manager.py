import threading
from pynput import keyboard, mouse

class InputManager:
    def __init__(self, tracker):
        self.tracker = tracker
        self.input_event = threading.Event()

    def input_loop(self):
        def on_press(key):
            self.tracker.on_action('keyboard')

        def on_click(x, y, button, pressed):
            if pressed:
                self.tracker.on_action('mouse_click')

        def on_move(x, y):
            self.tracker.on_action('selection')

        keyboard_listener = keyboard.Listener(on_press=on_press)
        mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)

        keyboard_listener.start()
        mouse_listener.start()

        while self.tracker.running:
            self.input_event.wait(1)  # Wait for 1 second or until set()
            self.input_event.clear()

        keyboard_listener.stop()
        mouse_listener.stop()
