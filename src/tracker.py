import threading
import logging
import traceback
from gui.gui_manager import GUIManager
from utils.input_manager import InputManager
from utils.data_manager import DataManager
from utils.settings_manager import SettingsManager

class APMTracker:
    def __init__(self):
        self.running = True
        self.data_manager = DataManager()
        self.settings_manager = SettingsManager()
        self.gui_manager = GUIManager(self)
        self.input_manager = InputManager(self)

    def run(self):
        try:
            # Import constants only when needed
            from utils.constants import DEFAULT_UPDATE_INTERVAL
            
            self.gui_manager.setup_gui()
            self.settings_manager.load_settings()
            self.input_thread = threading.Thread(target=self.input_manager.input_loop, daemon=True)
            self.input_thread.start()
            self.gui_manager.update_gui()
            self.gui_manager.run_main_loop()
        except Exception as e:
            logging.error(f"Error in run method: {str(e)}")
            logging.debug(traceback.format_exc())
            raise

    def on_closing(self):
        self.settings_manager.save_settings()
        self.running = False
        self.input_manager.input_event.set()  # Ensure input_loop exits
        self.input_thread.join()
        self.gui_manager.root.quit()

    def on_action(self, action_type):
        self.data_manager.record_action(action_type)
        self.gui_manager.graph_needs_update = True
        self.input_manager.input_event.set()
