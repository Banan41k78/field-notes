"""Модели записанного трека."""
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from models.geo import haversine_m


@dataclass
class TrackPoint:
    """Одна точка GPS-трека."""
    lat: float
    lon: float
    timestamp: str  # ISO 8601, например "2026-11-09T14:23:01"
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


@dataclass
class Track:
    """Записанный трек: набор точек + метаданные."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )
    points: list[TrackPoint] = field(default_factory=list)
    synced: bool = False

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
    def duration_sec(self) -> int:
        if self.is_empty:
            return 0
        try:
            start = datetime.fromisoformat(self.points[0].timestamp)
            end = datetime.fromisoformat(self.points[-1].timestamp)
            return max(0, int((end - start).total_seconds()))
        except (ValueError, TypeError):
            return 0

    @property
    def avg_speed_kmh(self) -> float:
        dur = self.duration_sec
        if dur == 0:
            return 0.0
        return self.distance_km / (dur / 3600.0)

    # ---------- Сериализация ----------

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
            created_at=d.get(
                "created_at", datetime.now().isoformat(timespec="seconds")
            ),
            synced=bool(d.get("synced", False)),
            points=[TrackPoint.from_dict(p) for p in d.get("points", [])],
        )

    # ---------- Утилиты ----------

    def auto_name(self) -> str:
        """Сгенерировать имя, если пользователь не задал своё."""
        if self.name:
            return self.name
        try:
            dt = datetime.fromisoformat(self.created_at)
            return dt.strftime("Трек %d.%m.%Y %H:%M")
        except (ValueError, TypeError):
            return "Без названия"