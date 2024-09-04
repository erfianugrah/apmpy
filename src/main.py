import logging
import os
from logging.handlers import RotatingFileHandler
import traceback
from tracker import APMTracker
from utils.constants import LOG_LEVELS
from utils.error_handler import safe_operation, APMTrackerError, handle_exception
import sys

# logging.basicConfig(level=logging.DEBUG)
# logging.debug(f"Current working directory: {os.getcwd()}")
# logging.debug(f"Script location: {os.path.abspath(__file__)}")

def setup_logging(log_level):
    """
    Set up logging with both file and console handlers, using log rotation.
    
    Args:
        log_level (int): The logging level to use.
    """
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_file = "apm_tracker.log"
    
    # Create a rotating file handler
    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(log_level)

    # Create a stream handler for console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(log_level)

    # Get the root logger and add the handlers
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

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
