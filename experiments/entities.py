from dataclasses import dataclass, field
from typing import List, Dict, Optional
from data import Metrics

@dataclass(frozen=True)
class Speaker:
    speaker_id: str
    name: str
    other_attributes: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Topic:
    topic_id: str
    name: str
    relevance: float  # A score or some measure of relevance to the conversation




@dataclass(frozen=True)
class Turn:
    turn_id: str
    start: str
    end: str
    duration: int
    sentences: List['Sentence'] = field(default_factory=list)
    metrics: Optional['Metrics'] = None

    def add_sentence(self, sentence: 'Sentence'):
        self.sentences.append(sentence)


@dataclass(frozen=True)
class Sentence:
    sentence_id: str
    text: str
    sentiment_score: Optional[float] = None
    words: List['Word'] = field(default_factory=list)

    def add_word(self, word: 'Word'):
        self.words.append(word)

# Aggregate Root
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
