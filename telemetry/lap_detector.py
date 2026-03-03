class LapDetector:
    """
    Detects lap completion based on completed_laps counter
    """
    def __init__(self):
        self.last_completed_laps = 0
        self.current_lap = 0

    def update(self, completed_laps: int):
        """
        Returns True if a new lap has been completed.
        """
        if completed_laps > self.last_completed_laps:
            self.last_completed_laps = completed_laps
            self.current_lap = completed_laps
            return True
        return False