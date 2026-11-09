# models/track.py
from dataclasses import dataclass, field
from datetime import datetime
from math import radians, sin, cos, asin, sqrt
import uuid

@dataclass
class TrackPoint:
    lat: float
    lon: float
    timestamp: str  # ISO 8601
    altitude: float | None = None
    speed_kmh: float | None = None

    def to_dict(self) -> dict:
        return {
            "lat": self.lat,
            "lon": self.lon,
            "timestamp": self.timestamp,
            "altitude": self.altitude,
            "speed_kmh": self.speed_kmh,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TrackPoint":
        return cls(
            lat=float(d["lat"]),
            lon=float(d["lon"]),
            timestamp=d["timestamp"],
            altitude=float(d["altitude"]) if d.get("altitude") is not None else None,
            speed_kmh=float(d["speed_kmh"]) if d.get("speed_kmh") is not None else None,
        )


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Расстояние между двумя точками в метрах (haversine)."""
    R = 6_371_000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 2 * R * asin(sqrt(a))


@dataclass
class Track:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    points: list[TrackPoint] = field(default_factory=list)
    synced: bool = False

    @property
    def distance_m(self) -> float:
        if len(self.points) < 2:
            return 0.0
        total = 0.0
        for a, b in zip(self.points, self.points[1:]):
            total += haversine_m(a.lat, a.lon, b.lat, b.lon)
        return total

    @property
    def distance_km(self) -> float:
        return self.distance_m / 1000.0

    @property
    def duration_sec(self) -> int:
        if len(self.points) < 2:
            return 0
        try:
            start = datetime.fromisoformat(self.points[0].timestamp)
            end = datetime.fromisoformat(self.points[-1].timestamp)
            return int((end - start).total_seconds())
        except (ValueError, TypeError):
            return 0

    @property
    def avg_speed_kmh(self) -> float:
        dur = self.duration_sec
        if dur == 0:
            return 0.0
        return (self.distance_m / 1000.0) / (dur / 3600.0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "synced": self.synced,
            "points": [p.to_dict() for p in self.points],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Track":
        return cls(
            id=d.get("id", str(uuid.uuid4())),
            name=d.get("name", ""),
            created_at=d.get("created_at", datetime.now().isoformat(timespec="seconds")),
            synced=bool(d.get("synced", False)),
            points=[TrackPoint.from_dict(p) for p in d.get("points", [])],
        )