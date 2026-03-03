import pandas as pd
import os


class LapStorage:
    def __init__(self, laps_path):
        self.laps_path = laps_path
        self.current_lap = 0
        self.df = self._empty_df()

    def _empty_df(self):
        return pd.DataFrame(columns=[
            "time",
            "speed_kmh",
            "rpm",
            "gear",
            "gas",
            "brake",
            "steer_angle"
        ])

    def start_new_lap(self, lap_number):
        self.current_lap = lap_number
        self.df = self._empty_df()

    def append(self, data):
        self.df = pd.concat([self.df, pd.DataFrame([data])], ignore_index=True)

    def save_lap(self):
        filename = f"lap_{self.current_lap:02d}.csv"
        path = os.path.join(self.laps_path, filename)
        self.df.to_csv(path, index=False)