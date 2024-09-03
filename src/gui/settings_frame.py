import tkinter as tk
from tkinter import ttk, messagebox
import logging
from utils.font_loader import get_font
from utils.constants import FONT_NAME, LABEL_FONT_SIZE

class SettingsFrame:
    def __init__(self, parent, tracker, custom_fonts):
        self.parent = parent
        self.tracker = tracker
        self.custom_fonts = custom_fonts
        self.frame = ttk.Frame(parent)
        self.setup_settings_frame()

    def setup_settings_frame(self):
        # Create a canvas that fills the entire frame
        canvas = tk.Canvas(self.frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create another frame inside the canvas
        inner_frame = ttk.Frame(canvas)

        # Add that frame to a window in the canvas
        canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        # Configure canvas and inner_frame
        def configure_inner_frame(event):
            # Update the width of the inner frame to match the canvas
            canvas.itemconfig(canvas_window, width=event.width)
            
        canvas.bind('<Configure>', configure_inner_frame)

        def on_frame_configure(event):
            # Reset the scroll region to encompass the inner frame
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner_frame.bind('<Configure>', on_frame_configure)

        # Bind mousewheel to scrolling only when the mouse is over the canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind('<Enter>', _bind_mousewheel)
        canvas.bind('<Leave>', _unbind_mousewheel)

        center_frame = ttk.Frame(inner_frame)
        center_frame.pack(expand=True)

        self.create_settings_widgets(center_frame)

        # Update the scrollregion when all widgets are in place
        inner_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def create_settings_widgets(self, parent):
        label_font = (FONT_NAME, LABEL_FONT_SIZE)
        entry_font = (FONT_NAME, LABEL_FONT_SIZE)
        button_font = (FONT_NAME, LABEL_FONT_SIZE, 'bold')

        ttk.Label(parent, text="Transparency:", font=label_font).pack(pady=5, padx=10, anchor="w")
        self.transparency_scale = ttk.Scale(parent, from_=0.1, to=1.0, orient=tk.HORIZONTAL, command=self.update_transparency)
        self.transparency_scale.set(self.tracker.settings_manager.transparency)
        self.transparency_scale.pack(pady=5, padx=10, fill="x")

        ttk.Label(parent, text="Target Program:", font=label_font).pack(pady=5, padx=10, anchor="w")
        self.target_program_combobox = ttk.Combobox(parent, values=self.tracker.settings_manager.window_list, font=entry_font)
        self.target_program_combobox.set(self.tracker.settings_manager.target_program)
        self.target_program_combobox.pack(pady=5, padx=10, fill="x")
        ttk.Button(parent, text="Set Target Program", command=self.set_target_program, style='TButton').pack(pady=5, padx=10)
        ttk.Button(parent, text="Clear Target Program", command=self.clear_target_program, style='TButton').pack(pady=5, padx=10)
        ttk.Button(parent, text="Refresh Window List", command=self.refresh_window_list, style='TButton').pack(pady=5, padx=10)

        ttk.Label(parent, text="Log Level:", font=label_font).pack(pady=5, padx=10, anchor="w")
        self.log_level_combobox = ttk.Combobox(parent, 
            values=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            font=entry_font)
        self.log_level_combobox.set(logging.getLevelName(self.tracker.settings_manager.log_level))
        self.log_level_combobox.pack(pady=5, padx=10, fill="x")
        ttk.Button(parent, text="Set Log Level", command=self.set_log_level, style='TButton').pack(pady=5, padx=10)

        ttk.Label(parent, text="Update Interval (ms):", font=label_font).pack(pady=5, padx=10, anchor="w")
        self.update_interval_entry = ttk.Entry(parent, font=entry_font)
        self.update_interval_entry.insert(0, str(self.tracker.settings_manager.update_interval))
        self.update_interval_entry.pack(pady=5, padx=10, fill="x")

        ttk.Label(parent, text="Graph Update Interval (ms):", font=label_font).pack(pady=5, padx=10, anchor="w")
        self.graph_update_interval_entry = ttk.Entry(parent, font=entry_font)
        self.graph_update_interval_entry.insert(0, str(self.tracker.settings_manager.graph_update_interval))
        self.graph_update_interval_entry.pack(pady=5, padx=10, fill="x")

        ttk.Label(parent, text="Graph Time Range:", font=label_font).pack(pady=5, padx=10, anchor="w")
        self.graph_time_range_var = tk.StringVar()
        self.graph_time_range_combobox = ttk.Combobox(parent, 
            textvariable=self.graph_time_range_var,
            values=[f"{t} seconds" for t in self.tracker.settings_manager.graph_time_range_options],
            font=entry_font)
        self.graph_time_range_combobox.set(f"{self.tracker.settings_manager.graph_time_range} seconds")
        self.graph_time_range_combobox.pack(pady=5, padx=10, fill="x")
        self.graph_time_range_combobox.bind("<<ComboboxSelected>>", self.on_graph_time_range_change)

        ttk.Label(parent, text="Max Actions Per Second:", font=label_font).pack(pady=5, padx=10, anchor="w")
        self.max_actions_per_second_entry = ttk.Entry(parent, font=entry_font)
        self.max_actions_per_second_entry.insert(0, str(self.tracker.settings_manager.max_actions_per_second))
        self.max_actions_per_second_entry.pack(pady=5, padx=10, fill="x")

        ttk.Label(parent, text="Action Cooldown (ms):", font=label_font).pack(pady=5, padx=10, anchor="w")
        self.action_cooldown_entry = ttk.Entry(parent, font=entry_font)
        self.action_cooldown_entry.insert(0, str(int(self.tracker.settings_manager.action_cooldown * 1000)))
        self.action_cooldown_entry.pack(pady=5, padx=10, fill="x")

        ttk.Label(parent, text="Effective Action Cooldown (ms):", font=label_font).pack(pady=5, padx=10, anchor="w")
        self.eaction_cooldown_entry = ttk.Entry(parent, font=entry_font)
        self.eaction_cooldown_entry.insert(0, str(int(self.tracker.settings_manager.eapm_cooldown * 1000)))
        self.eaction_cooldown_entry.pack(pady=5, padx=10, fill="x")

        ttk.Button(parent, text="Apply Settings", command=self.apply_settings, style='TButton').pack(pady=10, padx=10)

    def update_transparency(self, value):
        self.tracker.gui_manager.update_transparency(value)

    def set_target_program(self):
        selected_window = self.target_program_combobox.get()
        if selected_window:
            self.tracker.settings_manager.set_target_program(selected_window)
            logging.info(f"Target program set to: {self.tracker.settings_manager.target_program}")
        else:
            logging.warning("No window selected")

    def clear_target_program(self):
        self.tracker.settings_manager.clear_target_program()
        self.target_program_combobox.set('')
        logging.info("Target program cleared")

    def refresh_window_list(self):
        self.tracker.settings_manager.update_window_list()
        self.target_program_combobox['values'] = self.tracker.settings_manager.window_list

    def set_log_level(self):
        selected_level = self.log_level_combobox.get()
        if selected_level:
            self.tracker.settings_manager.set_log_level(selected_level)
            logging.info(f"Log level set to: {selected_level}")
        else:
            logging.warning("No log level selected")

    def on_graph_time_range_change(self, event):
        selected = self.graph_time_range_var.get()
        time_range = int(selected.split()[0])
        index = self.tracker.settings_manager.graph_time_range_options.index(time_range)
        self.tracker.settings_manager.set_graph_time_range(index)
        self.tracker.gui_manager.update_graph_settings()

    def apply_settings(self):
        try:
            new_settings = {
                'update_interval': int(self.update_interval_entry.get()),
                'graph_update_interval': int(self.graph_update_interval_entry.get()),
                'max_actions_per_second': int(self.max_actions_per_second_entry.get()),
                'action_cooldown': int(self.action_cooldown_entry.get()) / 1000,
                'eapm_cooldown': int(self.eaction_cooldown_entry.get()) / 1000
            }
            self.tracker.settings_manager.update_settings(**new_settings)
            self.tracker.gui_manager.update_graph_settings()
            logging.info("Settings applied successfully")
            messagebox.showinfo("Success", "Settings applied successfully")
        except ValueError as e:
            logging.error(f"Invalid input in settings: {str(e)}")
            messagebox.showerror("Error", "Please enter valid numbers for all settings.")
        except Exception as e:
            logging.error(f"Error applying settings: {str(e)}")
            messagebox.showerror("Error", f"An error occurred while applying settings: {str(e)}")
