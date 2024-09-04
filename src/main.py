import logging
import os
from logging.handlers import RotatingFileHandler
import traceback
from tracker import APMTracker
from utils.constants import LOG_LEVELS
from utils.error_handler import safe_operation, APMTrackerError, handle_exception
import sys

def setup_logging(log_level):
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_file = "apm_tracker.log"
    
    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Disable matplotlib debug logging
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

@safe_operation
def main():
    """
    Main function to initialize and run the APM Tracker.
    """
    tracker = APMTracker()
    tracker.settings_manager.load_settings()

    # Set up logging based on user settings
    setup_logging(tracker.settings_manager.log_level)

    logging.info("Starting APM Tracker")
    tracker.run()

if __name__ == "__main__":
    # Set the global exception handler
    sys.excepthook = handle_exception

    try:
        main()
    except APMTrackerError as e:
        logging.critical(f"Critical error in main: {str(e)}")
        logging.debug(traceback.format_exc())
    except Exception as e:
        logging.critical(f"Unexpected error in main: {str(e)}")
        logging.debug(traceback.format_exc())
    finally:
        logging.info("APM Tracker shutting down")
