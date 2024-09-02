import logging
import traceback
from tracker import APMTracker

# Set up logging
logging.basicConfig(filename='apm_tracker.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    try:
        tracker = APMTracker()
        tracker.run()
    except Exception as e:
        logging.critical(f"Critical error in main: {str(e)}")
        logging.debug(traceback.format_exc())
        print(f"A critical error occurred. Please check the log file for details: {str(e)}")
