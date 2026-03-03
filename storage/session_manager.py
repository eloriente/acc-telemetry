import os
from datetime import datetime
import json


class SessionManager:
    def __init__(self, base_path="data"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_path = os.path.join(base_path, timestamp)
        self.laps_path = os.path.join(self.session_path, "laps")

        os.makedirs(self.laps_path, exist_ok=True)

        self.session_info = {
            "start_time": timestamp,
            "laps_recorded": 0
        }

    def save_session_info(self):
        with open(os.path.join(self.session_path, "session.json"), "w") as f:
            json.dump(self.session_info, f, indent=4)

    def increment_lap(self):
        self.session_info["laps_recorded"] += 1
        self.save_session_info()