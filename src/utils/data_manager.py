import time
from collections import deque
import csv
import datetime
import logging
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
        self.action_buffer = deque(maxlen=5)
        self.action_cooldown = 0.05
        self.sequence_cooldown = 0.2
        self.lock = threading.RLock()

        self.hotkey_groups = {
            'control': set(['ctrl']),
            'shift': set(['shift']),
            'alt': set(['alt']),
            'numbers': set([str(i) for i in range(10)]),
            'letters': set([chr(i) for i in range(ord('a'), ord('z')+1)]),
            'f_keys': set([f'f{i}' for i in range(1, 13)]),
        }

        self.action_weights = {
            'control_group': 1.2,
            'build': 1.5,
            'train': 1.3,
            'research': 1.4,
            'attack': 1.1,
            'move': 0.9,
            'camera': 0.7,
            'select': 0.8,
            'ability': 1.2,
            'default': 1.0
        }

    def is_effective_action(self, action_type, key, current_time):
        if current_time - self.last_eapm_action_time < self.action_cooldown:
            return False, 'default'

        if len(self.action_buffer) >= 3:
            sequence_type = self.identify_sequence(list(self.action_buffer)[-3:])
            if sequence_type and current_time - self.last_eapm_action_time >= self.sequence_cooldown:
                return True, sequence_type

        if action_type == 'mouse_click':
            return True, 'default'
        elif action_type == 'keyboard':
            if self.is_in_hotkey_group(key, 'numbers'):
                return True, 'control_group'
            elif self.is_in_hotkey_group(key, 'letters') or self.is_in_hotkey_group(key, 'f_keys'):
                return True, 'ability'

        return False, 'default'

    def identify_sequence(self, sequence):
        if ((self.is_in_hotkey_group(sequence[0][1], 'control') or 
             self.is_in_hotkey_group(sequence[0][1], 'shift')) and
            self.is_in_hotkey_group(sequence[1][1], 'numbers')):
            return 'control_group'

        if (self.is_in_hotkey_group(sequence[0][1], 'numbers') and
            sequence[1][0] == 'mouse_click'):
            return 'control_group'

        if ((self.is_in_hotkey_group(sequence[0][1], 'letters') or 
             self.is_in_hotkey_group(sequence[0][1], 'f_keys')) and
            sequence[1][0] == 'mouse_click'):
            return 'build'

        if (self.is_in_hotkey_group(sequence[0][1], 'shift') and
            sequence[1][0] == 'mouse_click'):
            return 'move'

        if (self.is_in_hotkey_group(sequence[0][1], 'control') and
            self.is_in_hotkey_group(sequence[1][1], 'f_keys')):
            return 'camera'

        return None

    def is_in_hotkey_group(self, key, group):
        return key in self.hotkey_groups.get(group, set())

    def record_action(self, action_type, key=None):
        with self.lock:
            current_time = time.time()
            utc_time = datetime.datetime.utcnow()
            
            self.actions.append(current_time)
            self.utc_actions.append(utc_time)
            self.action_buffer.append((action_type, key))
            
            is_effective, action_category = self.is_effective_action(action_type, key, current_time)
            if is_effective:
                weight = self.action_weights.get(action_category, self.action_weights['default'])
                self.effective_actions.append((current_time, weight))
                self.utc_effective_actions.append((utc_time, weight))
                self.last_eapm_action_time = current_time
                self.last_action_type = action_type

            self.last_action_time = current_time

    def calculate_current_apm(self):
        current_time = time.time()
        minute_ago = current_time - 60
        return sum(1 for t in self.actions if t > minute_ago)

    def calculate_current_eapm(self):
        current_time = time.time()
        minute_ago = current_time - 60
        return sum(weight for t, weight in self.effective_actions if t > minute_ago)

    def calculate_average_apm(self):
        total_actions = len(self.actions)
        elapsed_time = (time.time() - self.start_time) / 60
        return total_actions / elapsed_time if elapsed_time > 0 else 0

    def calculate_average_eapm(self):
        total_effective_actions = sum(weight for _, weight in self.effective_actions)
        elapsed_time = (time.time() - self.start_time) / 60
        return total_effective_actions / elapsed_time if elapsed_time > 0 else 0

    def export_data(self, filename=None):
        if filename is None:
            filename = f"apm_data_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Action Type', 'Effective', 'Weight'])
            
            all_actions = (
                [(t, 'Regular', False, 1.0) for t in self.utc_actions] +
                [(t, 'Effective', True, w) for t, w in self.utc_effective_actions]
            )
            all_actions.sort(key=lambda x: x[0])

            for timestamp, action_type, effective, weight in all_actions:
                formatted_time = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                writer.writerow([formatted_time, action_type, effective, weight])
        
        return filename

    def current_time(self):
        return time.time()

    def format_timestamp(self, timestamp):
        return datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
