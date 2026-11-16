"""Тест связки LocationService + TrackRecorder + TrackStorage."""
import asyncio
import flet as ft

from app_context import AppContext
from config import load_settings
from services.mock_location_service import MockLocationService
from services.track_storage import TrackStorage
from services.track_recorder import TrackRecorder


async def main(page: ft.Page):
    prefs = ft.SharedPreferences()
    page.services.append(prefs)
    settings = await load_settings(prefs)
    ctx = AppContext(page=page, prefs=prefs, settings=settings)

    loc = MockLocationService(speed_kmh=5.0)
    storage = TrackStorage()
    recorder = TrackRecorder(ctx, loc, storage)

    print("Треков до записи:", storage.count())

    # Записываем 10 секунд
    track = await recorder.start()
    print("Запись начата, id:", track.id)
    await asyncio.sleep(10)
    saved = await recorder.stop()

    if saved:
        print(f"Сохранено: {saved.auto_name()}, "
              f"точек: {len(saved.points)}, "
              f"дистанция: {saved.distance_km:.3f} км, "
              f"длительность: {saved.duration_sec} сек")
    else:
        print("Трек пустой — не сохранён")

    print("Треков после записи:", storage.count())
    for t in storage.list():
        print(f"  - {t.auto_name()}: {len(t.points)} точек, {t.distance_km:.3f} км")


ft.run(main)