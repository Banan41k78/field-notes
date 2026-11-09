# models/track.py
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class TrackPoint:
    lat: float
    lon: float
    timestamp: str
    altitude: float | None = None
    speed_kmh: float | None = None

@dataclass
class Track:
    id: str
    name: str
    created_at: str
    points: list[TrackPoint] = field(default_factory=list)
    distance_m: float = 0.0
    duration_sec: int = 0
    synced: bool = False