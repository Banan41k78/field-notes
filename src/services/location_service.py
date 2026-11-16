"""Обёртка над flet-geolocator: разрешения, текущая позиция, поток обновлений."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

import flet as ft
import flet_geolocator as ftg

from config import GPSAccuracy


_ACCURACY_MAP = {
    GPSAccuracy.HIGH: ftg.GeolocatorPositionAccuracy.HIGH,
    GPSAccuracy.BALANCED: ftg.GeolocatorPositionAccuracy.BEST,
    GPSAccuracy.LOW: ftg.GeolocatorPositionAccuracy.LOW,
}


@dataclass
class Position:
    """Нормализованная позиция."""
    lat: float
    lon: float
    altitude: float | None
    speed_kmh: float | None
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "lat": self.lat,
            "lon": self.lon,
            "altitude": self.altitude,
            "speed_kmh": self.speed_kmh,
            "timestamp": self.timestamp,
        }

    def __repr__(self) -> str:
        return (
            f"Position({self.lat:.5f}, {self.lon:.5f}, "
            f"alt={self.altitude}, spd={self.speed_kmh} км/ч)"
        )


class LocationService:
    """
    Управляет доступом к GPS.

    В flet-geolocator 1.0.x нет методов start_tracking/stop_tracking.
    Поток обновлений работает постоянно, как только у Geolocator
    установлен on_position_change. Мы лишь включаем/выключаем приём
    через флаг _tracking.
    """

    def __init__(self, page: ft.Page, settings):
        self.page = page
        self.settings = settings

        self._permission: ftg.GeolocatorPermissionStatus | None = None
        self._tracking = False
        self._on_position: Callable[[Position], None] | None = None
        self._on_error: Callable[[str], None] | None = None

        self._geolocator = ftg.Geolocator(
            configuration=ftg.GeolocatorConfiguration(
                accuracy=_ACCURACY_MAP[settings.gps.accuracy],
                distance_filter=settings.gps.distance_filter,
            ),
            on_position_change=self._handle_position,
            on_error=self._handle_error,
        )
        page.services.append(self._geolocator)

    # ---------- Разрешения ----------

    async def request_permission(self) -> bool:
        """Запросить разрешение. В flet-geolocator 1.0.x метод без аргументов."""
        if self._permission in (
            ftg.GeolocatorPermissionStatus.WHILE_IN_USE,
            ftg.GeolocatorPermissionStatus.ALWAYS,
        ):
            return True

        try:
            self._permission = await self._geolocator.request_permission()
        except Exception as e:
            print(f"[LocationService] request_permission failed: {e}")
            self._permission = ftg.GeolocatorPermissionStatus.DENIED

        return self._permission in (
            ftg.GeolocatorPermissionStatus.WHILE_IN_USE,
            ftg.GeolocatorPermissionStatus.ALWAYS,
        )

    @property
    def has_permission(self) -> bool:
        return self._permission in (
            ftg.GeolocatorPermissionStatus.WHILE_IN_USE,
            ftg.GeolocatorPermissionStatus.ALWAYS,
        )

    # ---------- Текущая позиция ----------

    async def get_current_position(self) -> Position | None:
        if not await self.request_permission():
            return None
        try:
            raw = await self._geolocator.get_current_position()
            return self._normalize(raw)
        except Exception as e:
            print(f"[LocationService] get_current_position failed: {e}")
            return None

    # ---------- Включение/выключение приёма ----------

    async def start_tracking(
        self,
        on_position: Callable[[Position], None],
        on_error: Callable[[str], None] | None = None,
    ) -> bool:
        """
        Включить приём обновлений GPS.
        Поток уже работает на уровне контрола — здесь только сохраняем колбэк
        и поднимаем флаг _tracking.
        """
        if not await self.request_permission():
            if on_error:
                on_error("Нет разрешения на геолокацию")
            return False

        self._on_position = on_position
        self._on_error = on_error
        self._tracking = True
        return True

    async def stop_tracking(self) -> None:
        """Перестать принимать обновления."""
        self._tracking = False
        self._on_position = None
        self._on_error = None

    @property
    def is_tracking(self) -> bool:
        return self._tracking

    # ---------- Внутренние обработчики ----------

    def _handle_position(self, e) -> None:
        if not self._tracking or not self._on_position:
            return
        pos = self._normalize(e.position)
        if pos:
            self._on_position(pos)

    def _handle_error(self, e) -> None:
        msg = str(getattr(e, "data", "GPS error"))
        print(f"[LocationService] error: {msg}")
        if self._on_error:
            self._on_error(msg)

    @staticmethod
    def _normalize(raw) -> Position | None:
        try:
            lat = float(raw.latitude)
            lon = float(raw.longitude)

            alt = None
            if getattr(raw, "altitude", None) is not None:
                alt = float(raw.altitude)

            spd_kmh = None
            spd_mps = getattr(raw, "speed", None)
            if spd_mps is not None:
                spd_kmh = float(spd_mps) * 3.6

            ts_attr = getattr(raw, "timestamp", None)
            if ts_attr is not None and hasattr(ts_attr, "isoformat"):
                ts = ts_attr.isoformat()
            else:
                ts = datetime.now().isoformat(timespec="seconds")

            return Position(
                lat=lat, lon=lon,
                altitude=alt, speed_kmh=spd_kmh, timestamp=ts,
            )
        except (AttributeError, TypeError, ValueError) as e:
            print(f"[LocationService] normalize failed: {e}")
            return None