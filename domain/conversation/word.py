from dataclasses import dataclass
from typing import Optional
from .time_ranged_entity import TimeRangedEntity


@dataclass(frozen=True)
class Word(TimeRangedEntity):
    word: str
    score: float

# @dataclass(frozen=True)
# class Word:
#     word: str
#     position: int
#     part_of_speech: Optional[str] = None
#     ner_tag: Optional[str] = None
