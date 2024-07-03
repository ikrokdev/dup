import datetime
from dataclasses import dataclass

from .time_range import TimeRange


@dataclass(frozen=True)
class TimeRangedEntity:
    time_range: TimeRange

    @property
    def start(self) -> float:
        """
        Returns the start time of the entity.
        """
        return self.time_range.start

    @property
    def end(self) -> float:
        """
        Returns the end time of the entity.
        """
        return self.time_range.end

    @property
    def duration(self) -> float:
        """
        Calculates and returns the duration in seconds of the entity.
        """
        if self.start and self.end:
            return (self.end - self.start).total_seconds()
        return 0

    def update_time_range(self, new_start: float, new_end: float):
        """
        Update the entity's time range with new start and end times.
        """
        self.time_range.update(new_start, new_end)