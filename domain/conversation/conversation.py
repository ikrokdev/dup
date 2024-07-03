from dataclasses import dataclass, field
from typing import Dict, List, Optional
from domain.conversation.speaker import (Speaker, SpeakerTurn)
from domain.conversation.topic import Topic
from domain.conversation.metrics import Metrics


@dataclass(frozen=True)
class Conversation:
    conversation_id: str
    speakers: Dict[str, Speaker] = field(default_factory=dict)
    turns: List[SpeakerTurn] = field(default_factory=list)
    topics: List[Topic] = field(default_factory=list)  # Aggregate list of topics from all turns
    metrics: Optional[Metrics] = None

    def add_speaker(self, speaker: Speaker):
        self.speakers[speaker.speaker_id] = speaker

    def add_turn(self, turn: SpeakerTurn):
        self.turns.append(turn)
        self.topics.extend(turn.topics)  # Assuming we want to aggregate topics at the conversation level

    def calculate_metrics(self):
        # Placeholder for analysers calculation logic
        pass

    def find_topics(self, keyword: str) -> List[Topic]:
        # Method to find topics by keyword
        return [topic for topic in self.topics if keyword.lower() in topic.name.lower()]
