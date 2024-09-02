import os
import sys
from tkinter import PhotoImage
import platform
import win32gui
import win32con
import logging
import traceback

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
            print(f"Icon set successfully for {window.title()}")
        except Exception as e:
            print(f"Error setting icon: {e}")
    else:
        print("Icon file not found.")

def set_window_icon(window, icon_path):
    if icon_path:
        try:
            icon = PhotoImage(file=icon_path)
            window.iconphoto(True, icon)
            print(f"Icon set successfully for {window.title()}")
        except Exception as e:
            print(f"Error setting icon: {e}")
    else:
        print("Icon file not found.")

def update_window_list():
    window_list = []
    try:
        if platform.system() == 'Windows':
            def enum_window_callback(hwnd, window_list):
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                    window_list.append(win32gui.GetWindowText(hwnd))
            win32gui.EnumWindows(enum_window_callback, window_list)
        else:
            # For non-Windows systems
            window_list = os.popen("wmctrl -l | awk '{$1=$2=$3=""; print $0}'").read().splitlines()
        logging.info(f"Updated window list with {len(window_list)} items")
    except Exception as e:
        logging.error(f"Error updating window list: {str(e)}")
        logging.debug(traceback.format_exc())
    return window_list

def set_appwindow(root):
    hwnd = win32gui.GetParent(root.winfo_id())
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    style = style & ~win32con.WS_EX_TOOLWINDOW
    style = style | win32con.WS_EX_APPWINDOW
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
    root.wm_withdraw()
    root.after(10, lambda: root.wm_deiconify())
