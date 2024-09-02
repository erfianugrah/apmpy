import platform
import logging
import psutil

if platform.system() == 'Windows':
    try:
        import win32gui
        import win32con
        import win32process
    except ImportError:
        logging.error("Failed to import Windows-specific modules. Make sure pywin32 is installed.")

def update_window_list():
    window_list = []
    try:
        if platform.system() == 'Windows':
            def enum_window_callback(hwnd, window_list):
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        window_list.append(process.name())
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass  # Process not found or access denied, skip this window
            win32gui.EnumWindows(enum_window_callback, window_list)
        else:
            # For non-Windows systems
            window_list = [p.name() for p in psutil.process_iter(['name']) if p.info['name']]
        
        # Remove duplicates and sort
        window_list = sorted(set(window_list))
        logging.info(f"Updated window list with {len(window_list)} unique programs")
    except Exception as e:
        logging.error(f"Error updating window list: {str(e)}")
    return window_list

def set_appwindow(root):
    if platform.system() == 'Windows':
        try:
            hwnd = win32gui.GetParent(root.winfo_id())
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            style = style & ~win32con.WS_EX_TOOLWINDOW
            style = style | win32con.WS_EX_APPWINDOW
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
            root.wm_withdraw()
            root.after(10, lambda: root.wm_deiconify())
        except Exception as e:
            logging.error(f"Error setting app window style: {e}")
    else:
        logging.info("set_appwindow is only applicable on Windows systems.")
