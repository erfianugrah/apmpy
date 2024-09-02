import logging
import traceback
from tracker import APMTracker
from utils.constants import LOG_LEVELS

if __name__ == "__main__":
    tracker = APMTracker()
    tracker.settings_manager.load_settings()

    # Set up logging based on user settings
    logging.basicConfig(filename='apm_tracker.log', level=tracker.settings_manager.log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        tracker.run()
    except Exception as e:
        logging.critical(f"Critical error in main: {str(e)}")
        logging.debug(traceback.format_exc())
        print(f"A critical error occurred. Please check the log file for details: {str(e)}")
