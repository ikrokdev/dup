from dataclasses import dataclass
from datetime import datetime


@dataclass
class TimeRange:
    start: float
    end: float

    def __init__(self, start: float, end: float):
        """
        Initialize a TimeRange object with start and end times.
        """
        # if start > end:
        #    raise ValueError("Start time must be earlier than end time.")
        self.start = start
        self.end = end

    def update(self, new_start: float, new_end: float):
        """
        Update the time range with new start and end times.
        """
        # if new_start > new_end:
        #    raise ValueError("Start time must be earlier than end time.")

        self.start = min(self.start, new_start)
        self.end = max(self.end, new_end)
        return self
