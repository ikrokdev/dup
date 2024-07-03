from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass(frozen=True)
class Metrics:
    speed: Optional[float] = None
    word_count: Optional[int] = None
    other: Dict[str, float] = field(default_factory=dict)
