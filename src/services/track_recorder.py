"""Запись трека: старт / пауза / продолжение / стоп."""
from __future__ import annotations

from datetime import datetime

from app_context import AppContext
from config import MapMode # [!!!] Определить в конфиге
from models.track import Track, TrackPoint
from services.location_service import LocationService, Position
from services.track_storage import TrackStorage


class TrackRecorder:
    """
    Управляет записью трека поверх LocationService.
    Хранит точки в памяти, при stop() сохраняет в TrackStorage.
    """

    def __init__(
        self,
        ctx: AppContext,
        location: LocationService,
        storage: TrackStorage,
    ):
        self.ctx = ctx
        self.location = location
        self.storage = storage
        self._is_recording = False
        self._is_paused = False

    async def start(self) -> Track:
        """Начать новую запись. Возвращает созданный Track."""
        track = Track(
            name="",
            created_at=datetime.now().isoformat(timespec="seconds"),
        )
        self.ctx.current_track = track
        self.ctx.map_mode = MapMode.RECORDING
        self._is_recording = True
        self._is_paused = False

        ok = await self.location.start_tracking(
            on_position=self._on_position,
            on_error=self._on_error,
        )
        if not ok:
            self.ctx.current_track = None
            self.ctx.map_mode = MapMode.IDLE
            self._is_recording = False
            raise RuntimeError("Не удалось запустить GPS")
        return track

    def pause(self) -> None:
        if self._is_recording and not self._is_paused:
            self._is_paused = True

    def resume(self) -> None:
        if self._is_recording and self._is_paused:
            self._is_paused = False

    async def stop(self) -> Track | None:
        """Остановить запись. Вернуть сохранённый Track или None."""
        await self.location.stop_tracking()
        self._is_recording = False
        self._is_paused = False

        track = self.ctx.current_track
        self.ctx.current_track = None
        self.ctx.map_mode = MapMode.IDLE

        if track is None or track.is_empty:
            return None

        self.storage.save(track)
        return track

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    # ---------- Колбэки от LocationService ----------

    def _on_position(self, pos: Position) -> None:
        if not self._is_recording or self._is_paused:
            return
        track = self.ctx.current_track
        if track is None:
            return
        track.points.append(TrackPoint(
            lat=pos.lat,
            lon=pos.lon,
            timestamp=pos.timestamp,
            altitude=pos.altitude,
            speed_kmh=pos.speed_kmh,
        ))

    def _on_error(self, msg: str) -> None:
        print(f"[TrackRecorder] GPS error: {msg}")