import logging
import traceback
import tkinter as tk
from tkinter import messagebox

class APMTrackerError(Exception):
    """Base exception class for APM Tracker"""
    pass

def show_error_dialog(title, message):
    """Display an error dialog to the user"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showerror(title, message)
    root.destroy()

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log keyboard interrupt
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    error_msg = f"An unexpected error occurred:\n{exc_type.__name__}: {exc_value}"
    show_error_dialog("Error", error_msg)

# Set the global exception handler
import sys
sys.excepthook = handle_exception

def safe_operation(func):
    """Decorator for safer function execution with error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            logging.debug(traceback.format_exc())
            raise APMTrackerError(f"An error occurred in {func.__name__}: {str(e)}")
    return wrapper
