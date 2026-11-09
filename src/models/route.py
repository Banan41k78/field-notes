# models/route.py
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class RoutePoint:
    lat: float
    lon: float
    name: str | None = None
    description: str | None = None

    def to_dict(self) -> dict:
        return {
            "lat": self.lat,
            "lon": self.lon,
            "name": self.name,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RoutePoint":
        return cls(
            lat=float(d["lat"]),
            lon=float(d["lon"]),
            name=d.get("name"),
            description=d.get("description"),
        )


@dataclass
class Route:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    points: list[RoutePoint] = field(default_factory=list)
    mode: str = "pedestrian"  # pedestrian | bicycle | vehicle
    source: str = "manual"    # manual | gpx | desktop

    @property
    def distance_m(self) -> float:
        if len(self.points) < 2:
            return 0.0
        from models.track import haversine_m
        return sum(
            haversine_m(a.lat, a.lon, b.lat, b.lon)
            for a, b in zip(self.points, self.points[1:])
        )

    @property
    def distance_km(self) -> float:
        return self.distance_m / 1000.0

    @property
    def waypoints_count(self) -> int:
        return len(self.points)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "mode": self.mode,
            "source": self.source,
            "points": [p.to_dict() for p in self.points],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Route":
        return cls(
            id=d.get("id", str(uuid.uuid4())),
            name=d.get("name", ""),
            created_at=d.get("created_at", datetime.now().isoformat(timespec="seconds")),
            mode=d.get("mode", "pedestrian"),
            source=d.get("source", "manual"),
            points=[RoutePoint.from_dict(p) for p in d.get("points", [])],
        )