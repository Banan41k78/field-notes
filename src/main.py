# src/main.py
import flet as ft
from config import load_settings
from views.settings_views import build_settings_view, apply_theme

async def main(page: ft.Page):
    page.title = "GPS Трекер"

    # 1. Создаём сервис SharedPreferences ОДИН раз
    prefs = ft.SharedPreferences()
    # 2. Привязываем его к странице — без этого он не работает
    page.services.append(prefs)

    # 3. Загружаем настройки, передавая prefs
    settings = await load_settings(prefs)
    apply_theme(page, settings)

    # 4. Передаём prefs в экран настроек (и в другие места, где сохраняете)
    page.views.append(build_settings_view(page, settings, prefs))
    page.update()

ft.run(main)