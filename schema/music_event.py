from dataclasses import dataclass


@dataclass
class MusicEvent:

    time: float

    strength: float = 0.0

    band: str = "UNKNOWN"

    event_type: str = "UNKNOWN"

    pitch: str | None = None

    frequency: float | None = None

    chord: str | None = None

    section: str | None = None

    emotion: float = 0.0

    confidence: float = 0.0
