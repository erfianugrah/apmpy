import os
import sys
import logging
from tkinter import PhotoImage

def get_icon_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        logging.debug(f"Running as frozen application. Base path: {base_path}")
    else:
        # Go up one more directory level
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logging.debug(f"Running as script. Base path: {base_path}")
    
    icon_path = os.path.join(base_path, 'icons', 'keebfire.png')
    logging.debug(f"Constructed icon path: {icon_path}")
    
    if os.path.exists(icon_path):
        logging.debug(f"Icon file found at: {icon_path}")
    else:
        logging.debug(f"Icon file not found at: {icon_path}")
        # List contents of base directory and icons directory (if it exists)
        logging.debug(f"Contents of {base_path}:")
        for item in os.listdir(base_path):
            logging.debug(f"  {item}")
        icons_dir = os.path.join(base_path, 'icons')
        if os.path.exists(icons_dir):
            logging.debug(f"Contents of {icons_dir}:")
            for item in os.listdir(icons_dir):
                logging.debug(f"  {item}")
        else:
            logging.debug(f"Icons directory does not exist: {icons_dir}")
    
    return icon_path if os.path.exists(icon_path) else None

def set_window_icon(window, icon_path):
    if icon_path:
        try:
            icon = PhotoImage(file=icon_path)
            window.iconphoto(True, icon)
            logging.info(f"Icon set successfully for {window.title()}")
        except Exception as e:
            logging.error(f"Error setting icon: {e}")
    else:
        logging.warning("Icon file not found.")
