import os
import sys
import logging
from tkinter import PhotoImage

def get_icon_path():
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app 
        # path into variable _MEIPASS'.
        base_path = sys._MEIPASS
    else:
        # If the application is run in a normal Python environment
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    icon_path = os.path.join(base_path, 'icons', 'keebfire.png')
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
