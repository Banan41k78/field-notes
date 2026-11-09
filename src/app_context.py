"""Общие объекты, доступные всем экранам."""
from dataclasses import dataclass

import flet as ft

from config import AppSettings


@dataclass
class AppContext:
    page: ft.Page
    prefs: ft.SharedPreferences
    settings: AppSettings