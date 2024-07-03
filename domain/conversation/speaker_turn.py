from dataclasses import dataclass, field
from typing import List, Optional

from .word import Word
from .time_ranged_entity import TimeRangedEntity
from .topic import Topic
from .sentence import Sentence


@dataclass(frozen=True)
class SpeakerTurn(TimeRangedEntity):
    turn_id: str
    speaker_id: str
    text: str
    sentences: List[Sentence] = field(default_factory=list)
    words: List[Word] = field(default_factory=list)
    topics: List[Topic] = field(default_factory=list)  # Topics discussed in this turn
    metrics: Optional['Metrics'] = None

    def add_topics(self, topics):
        self.topics.extend(topics)

    def add_topic(self, topic: Topic):
        self.topics.append(topic)

    def add_sentence(self, sentence: Sentence):
        self.sentences.append(sentence)

    def add_word(self, word: 'Word', position: Optional[int] = None):
        if position is None or position > len(self.words):
            self.words.append(word)
        else:
            self.words.insert(position, word)
