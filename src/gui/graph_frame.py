import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import datetime
from utils.constants import (
    GRAPH_APM_COLOR, GRAPH_EAPM_COLOR, GRAPH_ALPHA, GRAPH_DPI, GRAPH_FIGSIZE,
    FONT_FILENAME, FONT_NAME, FONT_PATH
)

class GraphFrame:
    def __init__(self, parent, tracker):
        self.parent = parent
        self.tracker = tracker
        self.frame = ttk.Frame(parent)
        self.setup_graph_frame()

    def setup_graph_frame(self):
        plt.rcParams['font.family'] = "monospace" 
        plt.rcParams['font.size'] = 10  # Base font size

        self.figure, self.ax = plt.subplots(figsize=GRAPH_FIGSIZE, dpi=GRAPH_DPI)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.apm_data = np.zeros(self.tracker.settings_manager.graph_time_range)
        self.eapm_data = np.zeros(self.tracker.settings_manager.graph_time_range)

        x = range(self.tracker.settings_manager.graph_time_range)
        self.apm_bars = self.ax.bar(x, self.apm_data, color=GRAPH_APM_COLOR, alpha=GRAPH_ALPHA, label='APM')
        self.eapm_bars = self.ax.bar(x, self.eapm_data, color=GRAPH_EAPM_COLOR, alpha=GRAPH_ALPHA, label='eAPM')

        self.ax.legend(loc='upper left', fontsize=8)
        self.ax.set_title('APM and eAPM over time', fontsize=12, fontweight='bold')
        self.ax.set_xlabel('Time (seconds ago)', fontsize=10)
        self.ax.set_ylabel('Number of Actions', fontsize=10)
        
        self.ax.set_xlim(self.tracker.settings_manager.graph_time_range - 1, 0)
        self.ax.set_ylim(0, self.tracker.settings_manager.max_actions_per_second)
        self.ax.set_xticks([0, self.tracker.settings_manager.graph_time_range // 4, self.tracker.settings_manager.graph_time_range // 2, 3 * self.tracker.settings_manager.graph_time_range // 4, self.tracker.settings_manager.graph_time_range - 1])
        self.ax.set_xticklabels(['0', str(self.tracker.settings_manager.graph_time_range // 4), str(self.tracker.settings_manager.graph_time_range // 2), str(3 * self.tracker.settings_manager.graph_time_range // 4), str(self.tracker.settings_manager.graph_time_range)], fontsize=8)
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
        self.apm_bars = self.ax.bar(x, self.apm_data, color=GRAPH_APM_COLOR, alpha=GRAPH_ALPHA, label='APM')
        self.eapm_bars = self.ax.bar(x, self.eapm_data, color=GRAPH_EAPM_COLOR, alpha=GRAPH_ALPHA, label='eAPM')

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
    
    def export_graph(self):
        try:
            # Create a new figure for export (to avoid modifying the displayed graph)
            fig, ax = plt.subplots(figsize=(10, 6))

            current_time = self.tracker.data_manager.current_time()
            x = np.arange(self.tracker.settings_manager.graph_time_range)
            
            apm_data = np.zeros(self.tracker.settings_manager.graph_time_range)
            eapm_data = np.zeros(self.tracker.settings_manager.graph_time_range)

            for t in self.tracker.data_manager.actions:
                if current_time - t <= self.tracker.settings_manager.graph_time_range:
                    index = int(current_time - t)
                    if index < self.tracker.settings_manager.graph_time_range:
                        apm_data[index] += 1

            for t in self.tracker.data_manager.effective_actions:
                if current_time - t <= self.tracker.settings_manager.graph_time_range:
                    index = int(current_time - t)
                    if index < self.tracker.settings_manager.graph_time_range:
                        eapm_data[index] += 1

            ax.bar(x, apm_data, color='blue', alpha=0.5, label='APM')
            ax.bar(x, eapm_data, color='green', alpha=0.5, label='eAPM')

            ax.legend(loc='upper left')
            ax.set_title('APM and eAPM over time')
            ax.set_xlabel('Time (seconds ago)')
            ax.set_ylabel('Number of Actions')
            ax.set_xlim(self.tracker.settings_manager.graph_time_range - 1, 0)

            # Add timestamp to the graph
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            plt.text(0.95, 0.05, f"Exported: {timestamp}",
                     horizontalalignment='right',
                     verticalalignment='bottom',
                     transform=ax.transAxes,
                     bbox=dict(facecolor='white', alpha=0.8),
                     fontsize=8)

            return fig

        except Exception as e:
            logging.error(f"Error creating graph for export: {str(e)}")
            return None
