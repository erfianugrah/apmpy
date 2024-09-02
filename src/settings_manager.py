import json
import logging
from utils import update_window_list

class SettingsManager:
    def __init__(self):
        self.target_program = ""
        self.transparency = 1.0
        self.window_list = []
        self.update_window_list()

    def save_settings(self):
        settings = {
            'target_program': self.target_program,
            'transparency': self.transparency
        }
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
        except IOError as e:
            logging.error(f"Error saving settings: {e}")

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.target_program = settings.get('target_program', '')
                self.transparency = settings.get('transparency', 1.0)
        except FileNotFoundError:
            logging.info("Settings file not found. Using defaults.")
        except json.JSONDecodeError:
            logging.error("Error decoding settings file. Using defaults.")

    def update_transparency(self, value):
        self.transparency = float(value)

    def set_target_program(self, program):
        self.target_program = program.lower()

    def clear_target_program(self):
        self.target_program = ""

    def update_window_list(self):
        self.window_list = update_window_list()
