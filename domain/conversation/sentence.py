from dataclasses import dataclass, field
from typing import List, Optional
from .time_ranged_entity import TimeRangedEntity
from .word import Word


@dataclass(frozen=True)
class Sentence(TimeRangedEntity):
    sentence_id: str
    speaker_id: str
    text: str
    sentiment_score: Optional[float] = None
    words: List[Word] = field(default_factory=list)
    ner_tags: Optional[List[str]] = field(default_factory=list)

    def add_word(self, word: 'Word', position: Optional[int] = None):
        """
        Add a word to the sentence. If position is specified, insert the word at that position.
        """
        if position is None or position > len(self.words):
            self.words.append(word)
        else:
            self.words.insert(position, word)
        # self._update_sentence_timing(word)

    def _update_sentence_timing(self, word: 'Word'):
        """
        Update the sentence's time range based on the words it contains.
        """
        if self.words:
            self.update_time_range(min(word.start for word in self.words),
                                   max(word.end for word in self.words))
