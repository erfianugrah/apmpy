import yaml
import logging
from utils.window_utils import update_window_list
from utils.constants import (
    DEFAULT_TRANSPARENCY, DEFAULT_UPDATE_INTERVAL, DEFAULT_GRAPH_UPDATE_INTERVAL,
    DEFAULT_GRAPH_TIME_RANGE, DEFAULT_MAX_ACTIONS_PER_SECOND,
    DEFAULT_ACTION_COOLDOWN, DEFAULT_EAPM_COOLDOWN, GRAPH_TIME_RANGE_OPTIONS
)

class SettingsManager:
    def __init__(self):
        self.target_program = ""
        self.transparency = DEFAULT_TRANSPARENCY
        self.window_list = []
        self.log_level = logging.INFO
        self.update_interval = DEFAULT_UPDATE_INTERVAL
        self.graph_update_interval = DEFAULT_GRAPH_UPDATE_INTERVAL
        self.graph_time_range = DEFAULT_GRAPH_TIME_RANGE
        self.max_actions_per_second = DEFAULT_MAX_ACTIONS_PER_SECOND
        self.action_cooldown = DEFAULT_ACTION_COOLDOWN
        self.eapm_cooldown = DEFAULT_EAPM_COOLDOWN
        self.graph_time_range_options = GRAPH_TIME_RANGE_OPTIONS
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
            with open('settings.yaml', 'w') as f:
                yaml.dump(settings, f, default_flow_style=False)
            logging.info("Settings saved successfully")
        except IOError as e:
            logging.error(f"Error saving settings: {e}")

    def load_settings(self):
        try:
            with open('settings.yaml', 'r') as f:
                settings = yaml.safe_load(f)
                self.target_program = settings.get('target_program', '')
                self.transparency = settings.get('transparency', DEFAULT_TRANSPARENCY)
                self.log_level = getattr(logging, settings.get('log_level', 'INFO'))
                self.update_interval = settings.get('update_interval', DEFAULT_UPDATE_INTERVAL)
                self.graph_update_interval = settings.get('graph_update_interval', DEFAULT_GRAPH_UPDATE_INTERVAL)
                self.graph_time_range = settings.get('graph_time_range', DEFAULT_GRAPH_TIME_RANGE)
                self.max_actions_per_second = settings.get('max_actions_per_second', DEFAULT_MAX_ACTIONS_PER_SECOND)
                self.action_cooldown = settings.get('action_cooldown', DEFAULT_ACTION_COOLDOWN)
                self.eapm_cooldown = settings.get('eapm_cooldown', DEFAULT_EAPM_COOLDOWN)
            logging.info("Settings loaded successfully")
        except FileNotFoundError:
            logging.info("Settings file not found. Using defaults.")
        except yaml.YAMLError as e:
            logging.error(f"Error parsing settings file: {e}")

    def update_transparency(self, value):
        self.transparency = float(value)
        logging.info(f"Transparency updated to {self.transparency}")

    def set_target_program(self, program):
        # Extract just the program name from the window title
        program_name = program.split(' — ')[0] if ' — ' in program else program
        self.target_program = program_name.lower()
        logging.info(f"Target program set to: {self.target_program}")
        self.save_settings()

    def clear_target_program(self):
        self.target_program = ""
        logging.info("Target program cleared")

    def update_window_list(self):
        try:
            self.window_list = update_window_list()
            logging.info(f"Window list updated. {len(self.window_list)} windows found.")
        except Exception as e:
            logging.error(f"Failed to update window list: {str(e)}")
            self.window_list = []  # Reset to empty list on failure

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
        self.validate_settings()  # Validate settings after update
        self.save_settings()  # Automatically save settings after update

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
    
    def set_graph_time_range(self, index):
        self.graph_time_range = self.graph_time_range_options[index]
        logging.info(f"Graph time range set to {self.graph_time_range} seconds")
