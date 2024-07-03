from dataclasses import dataclass, field
from typing import List
from .speaker_turn import SpeakerTurn


@dataclass
class Speaker:
    speaker_id: str
    name: str
    turns: List[SpeakerTurn] = field(default_factory=list)

    def filter_turns(self, start_time: float = None, end_time: float = None):
        """
        Filter turns based on start and end times.
        """
        filtered_turns = [turn for turn in self.turns if (start_time is None or turn.start >= start_time) and
                          (end_time is None or turn.end <= end_time)]
        return filtered_turns

    def add_turn(self, turn: SpeakerTurn):
        self.turns.append(turn)
