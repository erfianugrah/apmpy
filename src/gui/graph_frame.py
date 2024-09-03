import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np

class GraphFrame:
    def __init__(self, parent, tracker):
        self.parent = parent
        self.tracker = tracker
        self.frame = ttk.Frame(parent)
        self.setup_graph_frame()

    def setup_graph_frame(self):
        self.figure, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.apm_data = np.zeros(self.tracker.settings_manager.graph_time_range)
        self.eapm_data = np.zeros(self.tracker.settings_manager.graph_time_range)

        x = range(self.tracker.settings_manager.graph_time_range)
        self.apm_bars = self.ax.bar(x, self.apm_data, color='blue', alpha=0.5, label='APM')
        self.eapm_bars = self.ax.bar(x, self.eapm_data, color='green', alpha=0.5, label='eAPM')

        self.ax.legend(loc='upper left')
        self.ax.set_title('APM and eAPM over time')
        self.ax.set_xlabel('Time (seconds ago)')
        self.ax.set_ylabel('Number of Actions')
        
        self.ax.set_xlim(self.tracker.settings_manager.graph_time_range - 1, 0)
        self.ax.set_ylim(0, self.tracker.settings_manager.max_actions_per_second)
        self.ax.set_xticks([0, self.tracker.settings_manager.graph_time_range // 4, self.tracker.settings_manager.graph_time_range // 2, 3 * self.tracker.settings_manager.graph_time_range // 4, self.tracker.settings_manager.graph_time_range - 1])
        self.ax.set_xticklabels(['0', str(self.tracker.settings_manager.graph_time_range // 4), str(self.tracker.settings_manager.graph_time_range // 2), str(3 * self.tracker.settings_manager.graph_time_range // 4), str(self.tracker.settings_manager.graph_time_range)])
        self.ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=5))

        self.ani = animation.FuncAnimation(
            self.figure, 
            self.update_graph, 
            interval=self.tracker.settings_manager.graph_update_interval, 
            blit=True, 
            save_count=100
        )

    def update_graph(self, frame):
        current_time = self.tracker.data_manager.current_time()
        new_apm_data = np.zeros(self.tracker.settings_manager.graph_time_range)
        new_eapm_data = np.zeros(self.tracker.settings_manager.graph_time_range)

        for t in self.tracker.data_manager.actions:
            if current_time - t <= self.tracker.settings_manager.graph_time_range:
                index = int(current_time - t)
                if index < self.tracker.settings_manager.graph_time_range:
                    new_apm_data[index] += 1

        for t in self.tracker.data_manager.effective_actions:
            if current_time - t <= self.tracker.settings_manager.graph_time_range:
                index = int(current_time - t)
                if index < self.tracker.settings_manager.graph_time_range:
                    new_eapm_data[index] += 1

        # Update bar heights
        for rect, h in zip(self.apm_bars, new_apm_data):
            rect.set_height(h)
        for rect, h in zip(self.eapm_bars, new_eapm_data):
            rect.set_height(h)

        # Dynamically adjust y-axis
        max_value = max(np.max(new_apm_data), np.max(new_eapm_data))
        y_max = min(max(max_value * 1.1, 1), self.tracker.settings_manager.max_actions_per_second)
        self.ax.set_ylim(0, y_max)

        # Update y-axis ticks
        self.ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=5))

        # Force redraw of the figure
        self.figure.canvas.draw()

        if not np.array_equal(new_apm_data, self.apm_data) or not np.array_equal(new_eapm_data, self.eapm_data):
            self.apm_data = new_apm_data
            self.eapm_data = new_eapm_data

            for rect, h in zip(self.apm_bars, self.apm_data):
                rect.set_height(h)
            for rect, h in zip(self.eapm_bars, self.eapm_data):
                rect.set_height(h)

            max_value = max(np.max(self.apm_data), np.max(self.eapm_data))
            y_max = min(max(max_value * 1.1, 1), self.tracker.settings_manager.max_actions_per_second)
            self.ax.set_ylim(0, y_max)
            self.ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=5))

            self.figure.canvas.draw()

        return self.apm_bars + self.eapm_bars

    def update_graph_settings(self):
        # Update graph based on new settings
        self.ax.clear()
        x = range(self.tracker.settings_manager.graph_time_range)
        self.apm_data = np.zeros(self.tracker.settings_manager.graph_time_range)
        self.eapm_data = np.zeros(self.tracker.settings_manager.graph_time_range)
        self.apm_bars = self.ax.bar(x, self.apm_data, color='blue', alpha=0.5, label='APM')
        self.eapm_bars = self.ax.bar(x, self.eapm_data, color='green', alpha=0.5, label='eAPM')

        self.ax.legend(loc='upper left')
        self.ax.set_title('APM and eAPM over time')
        self.ax.set_xlabel('Time (seconds ago)')
        self.ax.set_ylabel('Number of Actions')
        
        self.ax.set_xlim(self.tracker.settings_manager.graph_time_range - 1, 0)
        self.ax.set_ylim(0, self.tracker.settings_manager.max_actions_per_second)
        self.ax.set_xticks([0, self.tracker.settings_manager.graph_time_range // 2, self.tracker.settings_manager.graph_time_range - 1])
        self.ax.set_xticklabels(['0', str(self.tracker.settings_manager.graph_time_range // 2), str(self.tracker.settings_manager.graph_time_range)])
        self.ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=5))

        self.canvas.draw()
