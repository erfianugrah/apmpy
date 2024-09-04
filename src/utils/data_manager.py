import time
import csv
import datetime
from collections import deque
import threading

class DataManager:
    def __init__(self):
        self.actions = deque(maxlen=3600)
        self.effective_actions = deque(maxlen=3600)
        self.utc_actions = deque(maxlen=3600)
        self.utc_effective_actions = deque(maxlen=3600)
        self.last_action_time = 0
        self.last_eapm_action_time = 0
        self.last_action_type = None
        self.start_time = time.time()
        self.peak_apm = 0
        self.peak_eapm = 0
        self.action_cooldown = 0.05
        self.eapm_cooldown = 0.5
        self.lock = threading.RLock()

    def record_action(self, action_type):
        with self.lock:
            current_time = time.time()
            utc_time = datetime.datetime.utcnow()
            
            if action_type in ['keyboard', 'mouse_click']:
                if current_time - self.last_action_time >= self.action_cooldown:
                    self.actions.append(current_time)
                    self.utc_actions.append(utc_time)
                    self.last_action_time = current_time

            if self.is_effective_action(action_type, current_time):
                self.effective_actions.append(current_time)
                self.utc_effective_actions.append(utc_time)
                self.last_eapm_action_time = current_time
                self.last_action_type = action_type

    def is_effective_action(self, action_type, current_time):
        if (current_time - self.last_eapm_action_time < self.eapm_cooldown or
            action_type == self.last_action_type):
            return False

        if action_type in ['keyboard', 'mouse_click']:
            return True
        elif action_type == 'selection' and self.last_action_type != 'selection':
            return True

        return False

    def calculate_current_apm(self):
        current_time = time.time()
        minute_ago = current_time - 60
        return sum(1 for t in self.actions if t > minute_ago)

    def calculate_current_eapm(self):
        current_time = time.time()
        minute_ago = current_time - 60
        return sum(1 for t in self.effective_actions if t > minute_ago)

    def calculate_average_apm(self):
        total_actions = len(self.actions)
        elapsed_time = (time.time() - self.start_time) / 60  # in minutes
        return total_actions / elapsed_time if elapsed_time > 0 else 0

    def calculate_average_eapm(self):
        total_effective_actions = len(self.effective_actions)
        elapsed_time = (time.time() - self.start_time) / 60  # in minutes
        return total_effective_actions / elapsed_time if elapsed_time > 0 else 0

    def export_data(self, filename=None):
        if filename is None:
            filename = f"apm_data_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Action Type'])
            
            all_actions = (
                [(t, 'Regular Action') for t in self.utc_actions] +
                [(t, 'Effective Action') for t in self.utc_effective_actions]
            )
            all_actions.sort(key=lambda x: x[0])

            for timestamp, action_type in all_actions:
                formatted_time = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                writer.writerow([formatted_time, action_type])
        
        return filename

    def current_time(self):
        return time.time()

    def format_timestamp(self, timestamp):
        return datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
