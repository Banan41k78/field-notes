"""Модели запланированного маршрута."""
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from models.geo import haversine_m


# Допустимые режимы передвижения
ROUTE_MODES = ("pedestrian", "bicycle", "vehicle")


@dataclass
class RoutePoint:
    """Одна путевая точка маршрута."""
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
    """Запланированный маршрут: список точек + метаданные."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )
    points: list[RoutePoint] = field(default_factory=list)
    mode: str = "pedestrian"       # pedestrian | bicycle | vehicle
    source: str = "manual"         # manual | gpx | desktop

    # ---------- Вычисляемые свойства ----------

    @property
    def is_empty(self) -> bool:
        return len(self.points) < 2

    @property
    def distance_m(self) -> float:
        if self.is_empty:
            return 0.0
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

    @property
    def start_point(self) -> RoutePoint | None:
        return self.points[0] if self.points else None

    @property
    def end_point(self) -> RoutePoint | None:
        return self.points[-1] if self.points else None

    # ---------- Сериализация ----------

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
            created_at=d.get(
                "created_at", datetime.now().isoformat(timespec="seconds")
            ),
            mode=d.get("mode", "pedestrian"),
            source=d.get("source", "manual"),
            points=[RoutePoint.from_dict(p) for p in d.get("points", [])],
        )