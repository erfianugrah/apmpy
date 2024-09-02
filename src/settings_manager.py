import json
import logging
from utils import update_window_list

class SettingsManager:
    def __init__(self):
        self.target_program = ""
        self.transparency = 1.0
        self.window_list = []
        self.log_level = logging.INFO
        self.update_interval = 500
        self.graph_update_interval = 1000
        self.graph_time_range = 60
        self.max_actions_per_second = 10
        self.action_cooldown = 0.05
        self.eapm_cooldown = 0.5
        self.update_window_list()

    def save_settings(self):
        settings = {
            'target_program': self.target_program,
            'transparency': self.transparency,
            'log_level': logging.getLevelName(self.log_level),
            'update_interval': self.update_interval,
            'graph_update_interval': self.graph_update_interval,
            'graph_time_range': self.graph_time_range,
            'max_actions_per_second': self.max_actions_per_second,
            'action_cooldown': self.action_cooldown,
            'eapm_cooldown': self.eapm_cooldown
        }
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
            logging.info("Settings saved successfully")
        except IOError as e:
            logging.error(f"Error saving settings: {e}")

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.target_program = settings.get('target_program', '')
                self.transparency = settings.get('transparency', 1.0)
                self.log_level = getattr(logging, settings.get('log_level', 'INFO'))
                self.update_interval = settings.get('update_interval', 500)
                self.graph_update_interval = settings.get('graph_update_interval', 1000)
                self.graph_time_range = settings.get('graph_time_range', 60)
                self.max_actions_per_second = settings.get('max_actions_per_second', 10)
                self.action_cooldown = settings.get('action_cooldown', 0.05)
                self.eapm_cooldown = settings.get('eapm_cooldown', 0.5)
            logging.info("Settings loaded successfully")
        except FileNotFoundError:
            logging.info("Settings file not found. Using defaults.")
        except json.JSONDecodeError:
            logging.error("Error decoding settings file. Using defaults.")

    def update_transparency(self, value):
        self.transparency = float(value)
        logging.info(f"Transparency updated to {self.transparency}")

    def set_target_program(self, program):
        self.target_program = program.lower()
        logging.info(f"Target program set to: {self.target_program}")

    def clear_target_program(self):
        self.target_program = ""
        logging.info("Target program cleared")

    def update_window_list(self):
        self.window_list = update_window_list()
        logging.info(f"Window list updated. {len(self.window_list)} windows found.")

    def set_log_level(self, level):
        self.log_level = getattr(logging, level)
        logging.getLogger().setLevel(self.log_level)
        logging.info(f"Log level set to: {level}")

    def update_settings(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logging.info(f"Setting '{key}' updated to {value}")
            else:
                logging.warning(f"Unknown setting: {key}")
        self.save_settings()

    def validate_settings(self):
        # Add any necessary validation logic here
        if self.update_interval < 100:
            logging.warning("Update interval too low. Setting to 100ms.")
            self.update_interval = 100
        if self.graph_update_interval < 500:
            logging.warning("Graph update interval too low. Setting to 500ms.")
            self.graph_update_interval = 500
        if self.graph_time_range < 10 or self.graph_time_range > 300:
            logging.warning("Invalid graph time range. Setting to 60 seconds.")
            self.graph_time_range = 60
        if self.max_actions_per_second < 1:
            logging.warning("Invalid max actions per second. Setting to 1.")
            self.max_actions_per_second = 1
        if self.action_cooldown < 0.01 or self.action_cooldown > 1:
            logging.warning("Invalid action cooldown. Setting to 0.05 seconds.")
            self.action_cooldown = 0.05
        if self.eapm_cooldown < 0.1 or self.eapm_cooldown > 2:
            logging.warning("Invalid eAPM cooldown. Setting to 0.5 seconds.")
            self.eapm_cooldown = 0.5

    def get_settings_dict(self):
        return {
            'target_program': self.target_program,
            'transparency': self.transparency,
            'log_level': logging.getLevelName(self.log_level),
            'update_interval': self.update_interval,
            'graph_update_interval': self.graph_update_interval,
            'graph_time_range': self.graph_time_range,
            'max_actions_per_second': self.max_actions_per_second,
            'action_cooldown': self.action_cooldown,
            'eapm_cooldown': self.eapm_cooldown
        }
