from dataclasses import dataclass


@dataclass(frozen=True)
class Topic:
    topic_id: str
    name: str
    relevance: float  # A score or some measure of relevance to the conversation
