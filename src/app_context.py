"""Общие объекты, доступные всем экранам."""
from dataclasses import dataclass, field
import flet as ft

from config import AppSettings, MapMode
from models.track import Track
from models.route import Route


@dataclass
class AppContext:
    page: ft.Page
    prefs: ft.SharedPreferences
    settings: AppSettings

    # Состояние
    map_mode: MapMode = MapMode.IDLE
    active_route: Route | None = None
    current_track: Track | None = None