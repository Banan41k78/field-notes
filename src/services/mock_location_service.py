"""Фейковый LocationService для тестов."""
import asyncio
from datetime import datetime
from typing import Callable

from services.location_service import Position


class MockLocationService:
    def __init__(self, start_lat=55.751244, start_lon=37.618423,
                 speed_kmh=5.0, interval_sec=1.0):
        self._lat = start_lat
        self._lon = start_lon
        self._speed_kmh = speed_kmh
        self._interval = interval_sec
        self._task: asyncio.Task | None = None
        self._on_position: Callable[[Position], None] | None = None
        self._on_error: Callable[[str], None] | None = None
        self._tracking = False

    async def request_permission(self) -> bool:
        return True

    @property
    def has_permission(self) -> bool:
        return True

    async def get_current_position(self) -> Position:
        return self._make_position()

    async def start_tracking(self, on_position, on_error=None) -> bool:
        self._on_position = on_position
        self._on_error = on_error
        self._tracking = True
        self._task = asyncio.create_task(self._loop())
        return True

    async def stop_tracking(self) -> None:
        self._tracking = False
        if self._task:
            self._task.cancel()
            self._task = None
        self._on_position = None

    @property
    def is_tracking(self) -> bool:
        return self._tracking

    def _make_position(self) -> Position:
        return Position(
            lat=self._lat, lon=self._lon,
            altitude=150.0, speed_kmh=self._speed_kmh,
            timestamp=datetime.now().isoformat(timespec="seconds"),
        )

    async def _loop(self):
        while self._tracking:
            await asyncio.sleep(self._interval)
            delta_deg = (self._speed_kmh / 3600 * self._interval) / 111.0
            self._lat += delta_deg
            if self._on_position:
                self._on_position(self._make_position())